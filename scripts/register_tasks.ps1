
$RepoPath = "c:\GIT\TraderFund"
$PythonPath = (Get-Command python).Source

Write-Host "Registering TraderFund Regime Engine Tasks..."
Write-Host "Repo: $RepoPath"
Write-Host "Python: $PythonPath"

# 1. Warm-Up Task (08:45 IST)
# Runs in SHADOW mode locally to warm up state / valid data feed
$TaskName1 = "TF_Regime_Warmup"
$Cmd1 = "$PythonPath -u -m traderfund.run_regime --mode SHADOW"
Unregister-ScheduledTask -TaskName $TaskName1 -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -Action (New-ScheduledTaskAction -Execute $PythonPath -Argument "-u -m traderfund.run_regime --mode SHADOW" -WorkingDirectory $RepoPath) `
                       -Trigger (New-ScheduledTaskTrigger -Daily -At 08:45) `
                       -TaskName $TaskName1 `
                       -Description "TraderFund Regime Engine: Pre-Market Warmup (Shadow Mode)"

# 2. Live Trading (09:15 IST)
# Runs in ENFORCED mode
$TaskName2 = "TF_Regime_Live"
Unregister-ScheduledTask -TaskName $TaskName2 -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -Action (New-ScheduledTaskAction -Execute $PythonPath -Argument "-u -m traderfund.run_regime --mode ENFORCED" -WorkingDirectory $RepoPath) `
                       -Trigger (New-ScheduledTaskTrigger -Daily -At 09:15) `
                       -TaskName $TaskName2 `
                       -Description "TraderFund Regime Engine: Live Trading (Enforced Mode)"

# 3. Post-Market Analytics (15:45 IST)
# Runs offline analytics
$TaskName3 = "TF_Regime_Analytics"
Unregister-ScheduledTask -TaskName $TaskName3 -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -Action (New-ScheduledTaskAction -Execute $PythonPath -Argument "-u -m traderfund.run_regime --mode ANALYTICS" -WorkingDirectory $RepoPath) `
                       -Trigger (New-ScheduledTaskTrigger -Daily -At 15:45) `
                       -TaskName $TaskName3 `
                       -Description "TraderFund Regime Engine: Post-Market Regret Analysis"

Write-Host "Tasks Registered Successfully."
Get-ScheduledTask | Where-Object {$_.TaskName -like "TF_Regime_*"} | Format-Table TaskName, State
