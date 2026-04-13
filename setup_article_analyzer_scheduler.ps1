# Setup Article Analyzer Task Scheduler
# This script creates a Windows Task Scheduler task to pre-analyze articles 3 weeks in advance

param(
    [switch]$Remove,
    [switch]$Status,
    [string]$Schedule = "Daily"  # Daily, Weekly, or Manual
)

$TaskName = "Article Analyzer - Tweet Processor"
$ScriptPath = $PSScriptRoot
$BatchFile = Join-Path $ScriptPath "run_article_analyzer.bat"

function Show-TaskStatus {
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host "📊 ARTICLE ANALYZER TASK SCHEDULER STATUS" -ForegroundColor Cyan
    Write-Host "=================================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
        $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
        
        Write-Host "✅ Task Status: " -NoNewline -ForegroundColor Green
        Write-Host $task.State -ForegroundColor White
        
        Write-Host "📅 Last Run: " -NoNewline -ForegroundColor Blue
        if ($taskInfo.LastRunTime -eq $null) {
            Write-Host "Never" -ForegroundColor Yellow
        } else {
            Write-Host $taskInfo.LastRunTime -ForegroundColor White
        }
        
        Write-Host "🔄 Next Run: " -NoNewline -ForegroundColor Blue
        if ($taskInfo.NextRunTime -eq $null) {
            Write-Host "Not scheduled" -ForegroundColor Yellow
        } else {
            Write-Host $taskInfo.NextRunTime -ForegroundColor White
        }
        
        Write-Host "📊 Last Result: " -NoNewline -ForegroundColor Blue
        $resultCode = $taskInfo.LastTaskResult
        if ($resultCode -eq 0) {
            Write-Host "Success (0)" -ForegroundColor Green
        } elseif ($resultCode -eq 267009) {
            Write-Host "Success (267009)" -ForegroundColor Green
        } else {
            Write-Host "Error ($resultCode)" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "⚙️  Task Configuration:" -ForegroundColor Yellow
        $actions = Get-ScheduledTask -TaskName $TaskName | Select-Object -ExpandProperty Actions
        Write-Host "   Arguments: $($actions.Arguments)" -ForegroundColor Gray
        Write-Host "   Working Directory: $($actions.WorkingDirectory)" -ForegroundColor Gray
        
        $triggers = Get-ScheduledTask -TaskName $TaskName | Select-Object -ExpandProperty Triggers
        if ($triggers) {
            Write-Host "   Schedule: $($triggers[0].GetType().Name)" -ForegroundColor Gray
            if ($triggers[0].DaysInterval) {
                Write-Host "   Frequency: Every $($triggers[0].DaysInterval) day(s)" -ForegroundColor Gray
            }
            if ($triggers[0].StartBoundary) {
                Write-Host "   Start Time: $($triggers[0].StartBoundary)" -ForegroundColor Gray
            }
        }
        
    } catch {
        Write-Host "❌ Task not found: $TaskName" -ForegroundColor Red
        Write-Host "   Run this script without parameters to create the task." -ForegroundColor Yellow
    }
    
    Write-Host ""
}

function Remove-AnalyzerTask {
    Write-Host "🗑️  Removing Article Analyzer task..." -ForegroundColor Yellow
    
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ Task removed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to remove task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Create-AnalyzerTask {
    param([string]$ScheduleType)
    
    Write-Host "🔧 Creating Article Analyzer task..." -ForegroundColor Blue
    Write-Host "   Schedule: $ScheduleType" -ForegroundColor Gray
    Write-Host "   Script: $BatchFile" -ForegroundColor Gray
    Write-Host ""
    
    # Check if batch file exists
    if (-not (Test-Path $BatchFile)) {
        Write-Host "❌ Batch file not found: $BatchFile" -ForegroundColor Red
        Write-Host "   Make sure run_article_analyzer.bat exists in the same directory." -ForegroundColor Yellow
        return
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
    
    # Create trigger based on schedule type
    switch ($ScheduleType.ToLower()) {
        "daily" {
            # Run daily at 9:00 AM (3 hours before tweet posting at 11:30 AM)
            $trigger = New-ScheduledTaskTrigger -Daily -At "09:00"
            Write-Host "   ⏰ Scheduled: Daily at 9:00 AM" -ForegroundColor Green
        }
        "weekly" {
            # Run weekly on Monday at 9:00 AM
            $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "09:00"
            Write-Host "   ⏰ Scheduled: Weekly on Monday at 9:00 AM" -ForegroundColor Green
        }
        "manual" {
            # No automatic trigger - manual execution only
            $trigger = $null
            Write-Host "   ⏰ Scheduled: Manual execution only" -ForegroundColor Yellow
        }
        default {
            Write-Host "❌ Invalid schedule type: $ScheduleType" -ForegroundColor Red
            Write-Host "   Valid options: Daily, Weekly, Manual" -ForegroundColor Yellow
            return
        }
    }
    
    # Create principal (run as current user)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
    
    # Create settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    # Create and register the task
    try {
        if ($trigger) {
            $task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Pre-analyzes articles for Tweet Processor to ensure reliable tweet generation"
        } else {
            $task = New-ScheduledTask -Action $action -Principal $principal -Settings $settings -Description "Pre-analyzes articles for Tweet Processor to ensure reliable tweet generation (Manual execution)"
        }
        
        Register-ScheduledTask -TaskName $TaskName -InputObject $task | Out-Null
        
        Write-Host "✅ Task created successfully!" -ForegroundColor Green
        Write-Host ""
        
        # Show the new task status
        Show-TaskStatus
        
        # Provide usage instructions
        Write-Host "💡 Usage Instructions:" -ForegroundColor Cyan
        Write-Host "   • The task will analyze articles 3 weeks in advance" -ForegroundColor White
        Write-Host "   • This ensures tweet generation is always reliable" -ForegroundColor White
        Write-Host "   • Analysis results are cached in workflow_state.json" -ForegroundColor White
        Write-Host "   • Run manually: schtasks /run /tn `"$TaskName`"" -ForegroundColor White
        Write-Host "   • View logs: type analysis_log.txt" -ForegroundColor White
        Write-Host ""

    } catch {
        Write-Host "❌ Failed to create task: $($_.Exception.Message)" -ForegroundColor Red
    }
}
}

# Main execution
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "🔧 ARTICLE ANALYZER TASK SCHEDULER SETUP" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

if ($Status) {
    Show-TaskStatus
} elseif ($Remove) {
    Remove-AnalyzerTask
} else {
    Write-Host "🎯 Setting up automated article analysis..." -ForegroundColor Blue
    Write-Host "   This will pre-analyze articles 3 weeks in advance" -ForegroundColor Gray
    Write-Host "   to ensure reliable tweet generation." -ForegroundColor Gray
    Write-Host ""
    
    Create-AnalyzerTask -ScheduleType $Schedule
}

Write-Host "🔍 Quick Commands:" -ForegroundColor Cyan
Write-Host "   Status:  .\setup_article_analyzer_scheduler.ps1 -Status" -ForegroundColor Gray
Write-Host "   Remove:  .\setup_article_analyzer_scheduler.ps1 -Remove" -ForegroundColor Gray
Write-Host "   Daily:   .\setup_article_analyzer_scheduler.ps1 -Schedule Daily" -ForegroundColor Gray
Write-Host "   Weekly:  .\setup_article_analyzer_scheduler.ps1 -Schedule Weekly" -ForegroundColor Gray
Write-Host "   Manual:  .\setup_article_analyzer_scheduler.ps1 -Schedule Manual" -ForegroundColor Gray
Write-Host ""
