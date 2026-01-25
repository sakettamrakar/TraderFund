# Start India Momentum Runner
# This script starts the India momentum runner at market open (09:00 IST)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

# Change to project directory
Set-Location $projectRoot

# Activate virtual environment (if exists)
$venvPath = Join-Path $projectRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..."
    & $venvPath
}

# Create logs directory if not exists
$logsDir = Join-Path $projectRoot "logs\scheduler"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

# Log file
$logFile = Join-Path $logsDir "india_momentum_start.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Log start
Add-Content -Path $logFile -Value "$timestamp - Starting India Momentum Runner..."

try {
    # Start India momentum runner (runs in background)
    $pythonExe = "python"
    if (Test-Path (Join-Path $projectRoot "venv\Scripts\python.exe")) {
        $pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"
    }
    
    $runnerScript = Join-Path $projectRoot "observations\india_momentum_runner.py"
    
    # Start process in background
    $process = Start-Process -FilePath $pythonExe `
                             -ArgumentList $runnerScript `
                             -WorkingDirectory $projectRoot `
                             -PassThru `
                             -WindowStyle Hidden
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - India Momentum Runner started (PID: $($process.Id))"
    
    Write-Host "India Momentum Runner started successfully (PID: $($process.Id))"
    
} catch {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $errorMsg = $_.Exception.Message
    Add-Content -Path $logFile -Value "$timestamp - ERROR: $errorMsg"
    Write-Error "Failed to start India Momentum Runner: $errorMsg"
    exit 1
}
