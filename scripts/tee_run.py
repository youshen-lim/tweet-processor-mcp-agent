"""Run a command, streaming its combined stdout/stderr live to the console and a log file.

run_tweet_processor.bat used to redirect the run's output to a log and print the
log only after the run ended, so the window sat silent at "Console output
captured to:" for the whole run, which on 2026-11-18 looked like a 16-minute hang.
This streams instead, while still writing the per-run log.

Output bytes pass through unchanged (the log stays UTF-8, exactly as before), and
the exit code is the command's own, so the runner's exit-code logging still works.

Two things must never stall the run or the log:
- The console. Writing to a Windows console blocks while text is selected in the
  window (QuickEdit), so the console is fed from a queue on its own thread, and
  the log is written directly. A blocked or missing console only delays or drops
  the on-screen echo.
- A grandchild that inherited the output pipe (e.g. an MCP server the run
  started). The helper waits for the command itself, not for the pipe to close.

Usage: python scripts/tee_run.py <log_path> <command> [args...]
"""

import os
import queue
import subprocess
import sys
import threading

# After the command exits, how long to keep draining output still in the pipe
# (and then still queued for the console) before giving up.
DRAIN_GRACE_SECONDS = 5.0
# After Ctrl+C (which the command also receives), how long to let it exit cleanly.
INTERRUPT_GRACE_SECONDS = 10.0
# Most chunks waiting for the console (each up to 64 KB) before echo is dropped.
CONSOLE_QUEUE_CHUNKS = 256


def main(argv):
    if len(argv) < 3:
        print("usage: tee_run.py <log_path> <command> [args...]", file=sys.stderr)
        return 2
    log_path, cmd = argv[1], argv[2:]
    # Unbuffered so a Python child's output appears as it is printed, not in blocks.
    env = dict(os.environ, PYTHONUNBUFFERED="1")
    console = getattr(sys.stdout, "buffer", None)  # None when no stdout is attached
    # Bounded, so a console that stays blocked cannot grow memory without limit;
    # when full, on-screen echo is dropped (the log keeps everything).
    console_queue = queue.Queue(maxsize=CONSOLE_QUEUE_CHUNKS)
    log_lock = threading.Lock()  # only ever held for a file write, never for console I/O

    def console_writer():
        while True:
            chunk = console_queue.get()
            if chunk is None:
                return
            try:
                console.write(chunk)
                console.flush()
            except (OSError, ValueError):
                return  # console gone; the log is unaffected

    with open(log_path, "wb") as log:

        def emit(chunk):
            with log_lock:
                if not log.closed:
                    log.write(chunk)
                    log.flush()
            if console is not None:
                try:
                    console_queue.put_nowait(chunk)
                except queue.Full:
                    pass  # console is blocked; drop the echo, never the log

        echo = None
        if console is not None:
            echo = threading.Thread(target=console_writer, daemon=True)
            echo.start()

        def finish_console():
            if echo is not None:
                try:
                    console_queue.put(None, timeout=DRAIN_GRACE_SECONDS)
                except queue.Full:
                    return  # console still blocked; give up on the echo
                echo.join(timeout=DRAIN_GRACE_SECONDS)

        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        except OSError as e:
            emit(f"tee_run: could not start {cmd[0]!r}: {e}\n".encode("utf-8"))
            finish_console()
            return 127

        def pump():
            try:
                for chunk in iter(lambda: proc.stdout.read1(65536), b""):
                    emit(chunk)
            except (OSError, ValueError):
                pass

        reader = threading.Thread(target=pump, daemon=True)
        reader.start()
        try:
            code = proc.wait()
        except KeyboardInterrupt:
            try:
                code = proc.wait(timeout=INTERRUPT_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                proc.kill()
                code = proc.wait()
        reader.join(timeout=DRAIN_GRACE_SECONDS)
        with log_lock:
            log.close()  # under the lock, so a still-running reader stops writing cleanly
        finish_console()
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
