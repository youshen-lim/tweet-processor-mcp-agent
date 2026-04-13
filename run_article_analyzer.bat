@echo off
REM Article Analyzer - Batch script for Windows Task Scheduler
REM Pre-analyzes articles 3 weeks in advance for reliable tweet generation

echo ================================================================================
echo ARTICLE ANALYZER - Automated Analysis for Tweet Processor
echo ================================================================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Log the execution
echo [%date% %time%] Article analyzer started >> analysis_log.txt

REM Run the article analyzer
python run_article_analyzer.py --analyze-next

REM Log completion
echo [%date% %time%] Article analyzer completed with exit code %ERRORLEVEL% >> analysis_log.txt

REM Exit with the same code as the Python script
exit /b %ERRORLEVEL%
