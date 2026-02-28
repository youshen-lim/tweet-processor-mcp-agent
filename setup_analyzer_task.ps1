# Simple Article Analyzer Task Scheduler Setup
# Creates a Windows Task Scheduler task to pre-analyze articles

param(
    [switch]$Remove,
    [switch]$Status
)

$TaskName = "Article Analyzer - Tweet Processor"
$ScriptPath = $PSScriptRoot
$BatchFile = Join-Path $ScriptPath "run_article_analyzer.bat"

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "🔧 ARTICLE ANALYZER TASK SCHEDULER SETUP" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

if ($Status) {
    Write-Host "📊 Checking task status..." -ForegroundColor Blue
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
        $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
        
        Write-Host "✅ Task Status: $($task.State)" -ForegroundColor Green
        Write-Host "📅 Last Run: $($taskInfo.LastRunTime)" -ForegroundColor Blue
        Write-Host "🔄 Next Run: $($taskInfo.NextRunTime)" -ForegroundColor Blue
        Write-Host "📊 Last Result: $($taskInfo.LastTaskResult)" -ForegroundColor Blue
        
    } catch {
        Write-Host "❌ Task not found: $TaskName" -ForegroundColor Red
    }
    exit
}

if ($Remove) {
    Write-Host "🗑️  Removing Article Analyzer task..." -ForegroundColor Yellow
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ Task removed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to remove task: $($_.Exception.Message)" -ForegroundColor Red
    }
    exit
}

# Create the task
Write-Host "🔧 Creating Article Analyzer task..." -ForegroundColor Blue
Write-Host "   Script: $BatchFile" -ForegroundColor Gray

# Check if batch file exists
if (-not (Test-Path $BatchFile)) {
    Write-Host "❌ Batch file not found: $BatchFile" -ForegroundColor Red
    Write-Host "   Make sure run_article_analyzer.bat exists in the same directory." -ForegroundColor Yellow
    exit 1
}

# Remove existing task if it exists
try {
    Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop | Out-Null
    Write-Host "⚠️  Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
} catch {
    # Task doesn't exist, which is fine
}

# Create action
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatchFile`"" -WorkingDirectory $ScriptPath

# Create trigger - Weekly on Monday at 9:00 AM (3 days before tweet posting)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "09:00"

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Create and register the task
try {
    $task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Pre-analyzes articles for Tweet Processor to ensure reliable tweet generation"
    
    Register-ScheduledTask -TaskName $TaskName -InputObject $task | Out-Null
    
    Write-Host "✅ Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏰ Scheduled: Weekly (Monday) at 9:00 AM" -ForegroundColor Green
    Write-Host ""
    
    # Show the new task status
    $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
    Write-Host "📊 Task Details:" -ForegroundColor Cyan
    Write-Host "   Status: Ready" -ForegroundColor White
    Write-Host "   Next Run: $($taskInfo.NextRunTime)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "💡 Usage Instructions:" -ForegroundColor Cyan
    Write-Host "   • The task will analyze articles 3 weeks in advance" -ForegroundColor White
    Write-Host "   • This ensures tweet generation is always reliable" -ForegroundColor White
    Write-Host "   • Analysis results are cached in workflow_state.json" -ForegroundColor White
    Write-Host "   • Run manually: schtasks /run /tn `"$TaskName`"" -ForegroundColor White
    Write-Host "   • View logs: type analysis_log.txt" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "❌ Failed to create task: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "🔍 Quick Commands:" -ForegroundColor Cyan
Write-Host "   Status:  .\setup_analyzer_task.ps1 -Status" -ForegroundColor Gray
Write-Host "   Remove:  .\setup_analyzer_task.ps1 -Remove" -ForegroundColor Gray
Write-Host ""
