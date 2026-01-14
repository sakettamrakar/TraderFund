# Setup Windows Scheduled Tasks for India Momentum Runner
# This script creates scheduled tasks for automated market-hours operation
# MUST BE RUN AS ADMINISTRATOR

# Set error action preference
$ErrorActionPreference = "Stop"

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator. Please run PowerShell as Administrator and try again."
    exit 1
}

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

Write-Host "Setting up Windows Scheduled Tasks for India Momentum Runner..."
Write-Host "Project Root: $projectRoot"

# Task 1: Market Start (09:00 IST, Mon-Fri)
$taskName1 = "India_Momentum_Start"
$startScript = Join-Path $scriptDir "start_india_momentum.ps1"

Write-Host "`nCreating task: $taskName1"

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName1 -Confirm:$false -ErrorAction SilentlyContinue

# Create action
$action1 = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$startScript`"" `
    -WorkingDirectory $projectRoot

# Create trigger (Mon-Fri at 09:00)
$trigger1 = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday `
    -At 09:00AM

# Create settings
$settings1 = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

# Register task
Register-ScheduledTask `
    -TaskName $taskName1 `
    -Action $action1 `
    -Trigger $trigger1 `
    -Settings $settings1 `
    -Description "Start India Momentum Runner at market open (09:00 IST)" `
    -RunLevel Highest

Write-Host "Task '$taskName1' created successfully"

# Task 2: Market Close (15:45 IST, Mon-Fri)
$taskName2 = "India_Momentum_Stop"
$stopScript = Join-Path $scriptDir "stop_india_momentum.ps1"

Write-Host "`nCreating task: $taskName2"

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName2 -Confirm:$false -ErrorAction SilentlyContinue

# Create action
$action2 = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$stopScript`"" `
    -WorkingDirectory $projectRoot

# Create trigger (Mon-Fri at 15:45)
$trigger2 = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday `
    -At 03:45PM

# Create settings
$settings2 = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

# Register task
Register-ScheduledTask `
    -TaskName $taskName2 `
    -Action $action2 `
    -Trigger $trigger2 `
    -Settings $settings2 `
    -Description "Stop India Momentum Runner at market close (15:45 IST)" `
    -RunLevel Highest

Write-Host "Task '$taskName2' created successfully"

# Summary
Write-Host "`n========================================="
Write-Host "Scheduled Tasks Setup Complete!"
Write-Host "========================================="
Write-Host "Task 1: $taskName1"
Write-Host "  - Runs: Monday-Friday at 09:00 AM"
Write-Host "  - Action: Start India Momentum Runner"
Write-Host ""
Write-Host "Task 2: $taskName2"
Write-Host "  - Runs: Monday-Friday at 03:45 PM"
Write-Host "  - Action: Stop India Momentum Runner + Run EOD Review"
Write-Host ""
Write-Host "You can view these tasks in Task Scheduler (taskschd.msc)"
Write-Host "========================================="
