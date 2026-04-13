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

REM Display header
echo ============================================================================
echo TWEET PROCESSOR - AUTOMATED POSTING
echo ============================================================================
echo.
echo Timestamp: %date% %time%
echo Working Directory: %cd%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    echo.
    pause
    exit /b 1
)

echo Python version:
python --version
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

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Run tweet processor
echo Running tweet processor...
echo.
python run_tweet_processor.py --post

REM Capture exit code
set EXIT_CODE=%errorlevel%

echo.
echo ============================================================================
echo EXECUTION COMPLETE
echo ============================================================================
echo Exit Code: %EXIT_CODE%
echo Timestamp: %date% %time%
echo.

REM Log to file
echo [%date% %time%] Tweet processor executed with exit code %EXIT_CODE% >> posting_log.txt

REM Always pause to see output (helpful for debugging)
echo.
echo Press any key to close this window...
pause >nul

exit /b %EXIT_CODE%

