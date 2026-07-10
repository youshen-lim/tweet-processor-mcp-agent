@echo off
REM ============================================================================
REM Tweet Processor - Timeout-Protected Execution
REM ============================================================================
REM
REM This script runs the tweet processor with a 10-minute timeout to prevent
REM indefinite stalling when run via Task Scheduler or manually.
REM
REM Exit Codes:
REM   0   - Success
REM   1   - General error
REM   124 - Timeout (process killed after 10 minutes)
REM   130 - User interrupt (Ctrl+C)
REM
REM ============================================================================

cd /d "%~dp0"

echo ============================================================================
echo TWEET PROCESSOR - TIMEOUT-PROTECTED EXECUTION
echo ============================================================================
echo.
echo Start Time: %date% %time%
echo Timeout: 10 minutes (600 seconds)
echo.

REM Auto-sync articles from articles.docx if it was updated since last run.
REM --if-newer is a no-op unless articles.docx is newer than articles.md;
REM --clear-cache forces the workflow to re-read the regenerated articles.md.
echo Checking articles.docx for updates...
python scripts\convert_docx_to_md.py --if-newer --clear-cache
echo.

REM Run Python script with timeout using PowerShell
REM The timeout will forcefully kill the process if it exceeds 10 minutes
powershell -Command "& { $ErrorActionPreference = 'Stop'; try { $process = Start-Process -FilePath 'python' -ArgumentList 'run_tweet_processor.py', '--post' -PassThru -NoNewWindow -Wait -PassThru; $timeoutSeconds = 600; $waited = 0; while (!$process.HasExited -and $waited -lt $timeoutSeconds) { Start-Sleep -Seconds 1; $waited++ }; if (!$process.HasExited) { Write-Host ''; Write-Host 'WARNING: Process timed out after 10 minutes'; Write-Host 'Forcing termination...'; $process | Stop-Process -Force; Start-Sleep -Seconds 2; exit 124 } else { exit $process.ExitCode } } catch { Write-Host 'ERROR:' $_.Exception.Message; exit 1 } }"

set EXIT_CODE=%errorlevel%

echo.
echo ============================================================================
echo End Time: %date% %time%
echo.

if %EXIT_CODE%==124 (
    echo STATUS: TIMEOUT - Process exceeded 10-minute limit and was terminated
    echo.
    echo This indicates the application is stalling. Possible causes:
    echo   1. Network connectivity issues to Anthropic API
    echo   2. API rate limiting or service degradation
    echo   3. Firewall blocking outbound HTTPS connections
    echo.
    echo Troubleshooting steps:
    echo   1. Check internet connection
    echo   2. Verify Anthropic API key is valid
    echo   3. Check logs in logs/ directory for details
    echo   4. Try running again in a few minutes
) else if %EXIT_CODE%==0 (
    echo STATUS: SUCCESS - Process completed successfully
) else if %EXIT_CODE%==130 (
    echo STATUS: INTERRUPTED - Process was interrupted by user
) else (
    echo STATUS: ERROR - Process exited with code %EXIT_CODE%
    echo Check logs in logs/ directory for details
)

echo ============================================================================
echo.

REM Log result to posting log
echo [%date% %time%] Exit code: %EXIT_CODE% >> posting_log.txt

exit /b %EXIT_CODE%

