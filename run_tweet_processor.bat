@echo off
REM ============================================================================
REM Tweet Processor - Automated Posting Script (Windows Batch)
REM ============================================================================
REM
REM This script is designed to be run by Windows Task Scheduler
REM for automated tweet posting on a schedule.
REM
REM Usage:
REM   - Double-click to run manually
REM   - Configure in Task Scheduler for automated execution
REM
REM ============================================================================

REM Set working directory to script location
cd /d "%~dp0"

REM Force UTF-8 for Python I/O. Without this, redirecting output to a log file
REM makes Python fall back to cp1252, and the emoji in status messages would
REM crash the run with UnicodeEncodeError.
set PYTHONUTF8=1

REM Display header
echo ============================================================================
echo TWEET PROCESSOR - AUTOMATED POSTING
echo ============================================================================
echo.
echo Timestamp: %date% %time%
echo Working Directory: %cd%
echo.

REM Use the project's virtual environment interpreter so runs are pinned to the
REM tested package set. Falling back to system Python risks breakage from
REM unrelated upgrades in user site-packages (this broke the 2026-08-24 run).
set PYTHON_EXE=.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    echo WARNING: .venv not found; falling back to system Python
    set PYTHON_EXE=python
)

REM Check if Python is available
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    echo.
    pause
    exit /b 1
)

echo Python interpreter: %PYTHON_EXE%
"%PYTHON_EXE%" --version
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found
    echo Please copy .env.example to .env and configure your API keys
    echo.
    pause
    exit /b 1
)

echo Configuration: .env file found
echo.

REM Auto-sync articles from articles.docx if it was updated since last run.
REM --if-newer is a no-op unless articles.docx is newer than articles.md;
REM --clear-cache forces the workflow to re-read the regenerated articles.md.
REM Fail-open: if this step errors, we log it and still post the last-good
REM articles.md rather than skipping the week. The workflow's Option B sync is a
REM second safety net, and its URL validation is the final guard before posting.
echo Checking articles.docx for updates...
"%PYTHON_EXE%" scripts\convert_docx_to_md.py --if-newer --clear-cache
set SYNC_CODE=%errorlevel%
if "%SYNC_CODE%"=="0" (
    echo [%date% %time%] docx-sync OK ^(exit=0^) >> posting_log.txt
) else (
    echo WARNING: docx sync failed ^(exit=%SYNC_CODE%^); continuing with last-good articles.md
    echo [%date% %time%] docx-sync FAILED ^(exit=%SYNC_CODE%^) - using last-good articles.md >> posting_log.txt
)
echo.

REM Run tweet processor, capturing all console output (tweet preview, grounding
REM warnings, sanitizer notices) to a per-run log so scheduled runs are auditable.
if not exist "logs" mkdir logs
for /f "usebackq delims=" %%t in (`powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"`) do set RUN_TS=%%t
set CONSOLE_LOG=logs\console-%RUN_TS%.log
echo Running tweet processor...
echo Console output captured to: %CONSOLE_LOG%
echo.
"%PYTHON_EXE%" run_tweet_processor.py --post > "%CONSOLE_LOG%" 2>&1

REM Capture exit code
set EXIT_CODE=%errorlevel%

REM Echo the captured output so manual runs still show it in the window
type "%CONSOLE_LOG%"

echo.
echo ============================================================================
echo EXECUTION COMPLETE
echo ============================================================================
echo Exit Code: %EXIT_CODE%
echo Timestamp: %date% %time%
echo.

REM Log to file
echo [%date% %time%] Tweet processor executed with exit code %EXIT_CODE% (console: %CONSOLE_LOG%) >> posting_log.txt

REM Always pause to see output (helpful for debugging)
echo.
echo Press any key to close this window...
pause >nul

exit /b %EXIT_CODE%

