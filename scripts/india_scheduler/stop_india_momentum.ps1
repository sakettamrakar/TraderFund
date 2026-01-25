# Stop India Momentum Runner
# This script stops the India momentum runner at market close (15:45 IST)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

# Change to project directory
Set-Location $projectRoot

# Create logs directory if not exists
$logsDir = Join-Path $projectRoot "logs\scheduler"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

# Log file
$logFile = Join-Path $logsDir "india_momentum_stop.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Log stop attempt
Add-Content -Path $logFile -Value "$timestamp - Stopping India Momentum Runner..."

try {
    # Find India momentum runner process
    $processes = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*india_momentum_runner*"
    }
    
    if ($processes) {
        foreach ($proc in $processes) {
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            Add-Content -Path $logFile -Value "$timestamp - Stopping process PID: $($proc.Id)"
            
            # Send graceful termination signal (SIGTERM equivalent)
            $proc.CloseMainWindow() | Out-Null
            Start-Sleep -Seconds 5
            
            # Force kill if still running
            if (-not $proc.HasExited) {
                Stop-Process -Id $proc.Id -Force
                Add-Content -Path $logFile -Value "$timestamp - Force killed process PID: $($proc.Id)"
            } else {
                Add-Content -Path $logFile -Value "$timestamp - Process gracefully stopped PID: $($proc.Id)"
            }
        }
    } else {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $logFile -Value "$timestamp - No India Momentum Runner process found"
    }
    
    # Run EOD review generator
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - Running EOD review generator..."
    
    $pythonExe = "python"
    if (Test-Path (Join-Path $projectRoot "venv\Scripts\python.exe")) {
        $pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"
    }
    
    $eodScript = Join-Path $projectRoot "observations\eod_review_generator.py"
    
    & $pythonExe $eodScript
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - EOD review generation complete"
    
    Write-Host "India Momentum Runner stopped successfully"
    
} catch {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $errorMsg = $_.Exception.Message
    Add-Content -Path $logFile -Value "$timestamp - ERROR: $errorMsg"
    Write-Error "Failed to stop India Momentum Runner: $errorMsg"
    exit 1
}
