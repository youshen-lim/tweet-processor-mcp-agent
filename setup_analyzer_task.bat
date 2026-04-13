@echo off
REM Setup Article Analyzer Task Scheduler
REM Creates a Windows Task Scheduler task to pre-analyze articles 3 weeks in advance

echo ================================================================================
echo ARTICLE ANALYZER TASK SCHEDULER SETUP
echo ================================================================================
echo.

set TASK_NAME=Article Analyzer - Tweet Processor
set SCRIPT_DIR=%~dp0
set BATCH_FILE=%SCRIPT_DIR%run_article_analyzer.bat

REM Check if batch file exists
if not exist "%BATCH_FILE%" (
    echo ❌ Batch file not found: %BATCH_FILE%
    echo    Make sure run_article_analyzer.bat exists in the same directory.
    pause
    exit /b 1
)

echo 🔧 Creating Article Analyzer task...
echo    Script: %BATCH_FILE%
echo    Schedule: Weekly (Monday) at 9:00 AM
echo.

REM Remove existing task if it exists
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ⚠️  Task already exists. Removing old task...
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
)

REM Create the scheduled task
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "cmd.exe /c \"%BATCH_FILE%\"" ^
    /sc weekly ^
    /d MON ^
    /st 09:00 ^
    /ru "%USERNAME%" ^
    /rl highest ^
    /f

if %ERRORLEVEL% == 0 (
    echo ✅ Task created successfully!
    echo.
    echo ⏰ Scheduled: Weekly (Monday) at 9:00 AM
    echo.
    
    echo 📊 Task Details:
    schtasks /query /tn "%TASK_NAME%" /fo list | findstr /i "Task Name Status Next Run"
    echo.
    
    echo 💡 Usage Instructions:
    echo    • The task will analyze articles 3 weeks in advance
    echo    • This ensures tweet generation is always reliable
    echo    • Analysis results are cached in workflow_state.json
    echo    • Run manually: schtasks /run /tn "%TASK_NAME%"
    echo    • View logs: type analysis_log.txt
    echo.
    
    echo 🔍 Quick Commands:
    echo    Status:  schtasks /query /tn "%TASK_NAME%"
    echo    Remove:  schtasks /delete /tn "%TASK_NAME%" /f
    echo    Run:     schtasks /run /tn "%TASK_NAME%"
    echo.
    
) else (
    echo ❌ Failed to create task. Error code: %ERRORLEVEL%
    echo    Make sure you're running as Administrator if needed.
    pause
    exit /b 1
)

echo ✅ Setup complete! The Article Analyzer will run weekly on Monday at 9:00 AM.
pause
