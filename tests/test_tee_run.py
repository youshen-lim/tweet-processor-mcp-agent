"""
Tests for scripts/tee_run.py, the runner helper that streams a run's output to
the console and the per-run log while keeping the command's exit code.
"""

import importlib.util
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

TEE_RUN = Path(__file__).resolve().parent.parent / "scripts" / "tee_run.py"


def _import_tee_run():
    spec = importlib.util.spec_from_file_location("tee_run", TEE_RUN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(log_path, *cmd):
    return subprocess.run(
        [sys.executable, str(TEE_RUN), str(log_path), *cmd],
        capture_output=True, timeout=60,
    )


@pytest.mark.unit
class TestTeeRun:

    def test_output_goes_to_console_and_log_unchanged(self, tmp_path):
        log = tmp_path / "console.log"
        child = (
            "import sys; sys.stdout.buffer.write('ok 🐦 émoji\\n'.encode('utf-8')); "
            "sys.stdout.flush(); sys.stderr.write('err line\\n')"
        )
        result = _run(log, sys.executable, "-c", child)

        assert result.returncode == 0
        logged = log.read_bytes()
        assert "ok 🐦 émoji".encode("utf-8") in logged
        assert b"err line" in logged  # stderr is merged into the log
        assert result.stdout == logged  # console sees exactly what the log holds

    def test_exit_code_is_the_commands_own(self, tmp_path):
        result = _run(tmp_path / "console.log", sys.executable, "-c", "import sys; sys.exit(3)")
        assert result.returncode == 3

    def test_unstartable_command_is_logged_and_fails(self, tmp_path):
        log = tmp_path / "console.log"
        result = _run(log, str(tmp_path / "no-such-program.exe"))

        assert result.returncode == 127
        assert b"could not start" in log.read_bytes()

    def test_grandchild_holding_the_pipe_does_not_hang(self, tmp_path):
        # The command starts a long-lived grandchild that inherits its stdout, then
        # exits. The helper must return with the command's code, not wait for the
        # grandchild to close the pipe.
        log = tmp_path / "console.log"
        child = (
            "import subprocess, sys; "
            "g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
            "print('grandchild', g.pid, flush=True); sys.exit(5)"
        )
        start = time.monotonic()
        result = _run(log, sys.executable, "-c", child)
        elapsed = time.monotonic() - start
        try:
            assert result.returncode == 5
            assert elapsed < 30
            assert b"grandchild" in log.read_bytes()
        finally:
            pid = int(log.read_bytes().split(b"grandchild")[1].split()[0])
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)

    def test_no_stdout_still_logs(self, tmp_path, monkeypatch):
        # Under Task Scheduler stdout may be absent; the helper must still run and log.
        tee_run = _import_tee_run()
        monkeypatch.setattr(sys, "stdout", None)
        log = tmp_path / "console.log"

        code = tee_run.main(["tee_run.py", str(log), sys.executable, "-c", "print('logged'); raise SystemExit(4)"])

        assert code == 4
        assert b"logged" in log.read_bytes()

    def test_blocked_console_does_not_stall_the_run_or_log(self, tmp_path, monkeypatch):
        # Simulates a console frozen by a QuickEdit selection: every console write
        # blocks. The command must still finish, the log must be complete, and the
        # helper must return the command's exit code.
        tee_run = _import_tee_run()
        release = threading.Event()

        class BlockedConsole:
            def write(self, chunk):
                release.wait()

            def flush(self):
                pass

        monkeypatch.setattr(sys, "stdout", type("Out", (), {"buffer": BlockedConsole()})())
        monkeypatch.setattr(tee_run, "DRAIN_GRACE_SECONDS", 1.0)
        monkeypatch.setattr(tee_run, "CONSOLE_QUEUE_CHUNKS", 4)  # exercise the drop path
        log = tmp_path / "console.log"
        # ~1 MB of output: far more than an OS pipe buffer, so a reader blocked on
        # the console would also block the command.
        child = "import sys; [print('x' * 1000) for _ in range(1000)]; print('done'); sys.exit(6)"

        start = time.monotonic()
        try:
            code = tee_run.main(["tee_run.py", str(log), sys.executable, "-c", child])
        finally:
            release.set()
        assert code == 6
        assert time.monotonic() - start < 30
        lines = log.read_bytes().splitlines()
        assert lines == [b"x" * 1000] * 1000 + [b"done"]  # the log is complete, in order

    def test_missing_arguments_print_usage(self, tmp_path):
        result = subprocess.run([sys.executable, str(TEE_RUN)], capture_output=True, timeout=60)
        assert result.returncode == 2
        assert b"usage" in result.stderr
