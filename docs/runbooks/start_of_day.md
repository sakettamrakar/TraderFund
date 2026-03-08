# Start of Day (SOD) Runbook

**Trigger**: 08:30 IST (Market Open - 45m)
**Owner**: Operator (Human)

## 1. Environment Verification
- [ ] **Check VPN/Network**: Ensure stable internet connection.
- [ ] **Check API Credits**: Verify Alpha Vantage / SmartAPI token validity.
- [ ] **Check Disk Space**: Ensure sufficient space for logs and data.
- [ ] **Run Pre-Open Validation Sweep**:
    ```powershell
    foreach ($phase in 'ingestion','memory','research','evaluation','dashboard') {
        python -m traderfund.validation.validation_runner --phase $phase --hook sod_check --market US
        if ($LASTEXITCODE -ne 0) { break }
    }
    ```
    Review `logs/validation/*_sod_check_latest.json` if any phase exits non-zero.

## 2. Process Initialization
- [ ] **Start Ingestion**:
    ```powershell
    python bin/run-skill.py --skill ingestion --mode live
    ```
- [ ] **Start Momentum Engine** (if applicable):
    ```powershell
    python bin/run-skill.py --skill momentum --mode live
    ```

## 3. Core Processing (Post-Market)
- [ ] **Run Narrative Engine**:
    ```powershell
    python bin/run_narrative.py --market US
    ```
- [ ] **Run Decision Engine**:
    ```powershell
    python bin/run_decision.py --market US
    ```

## 3. Health Check
- [ ] **Verify Logs**: Check `logs/system.log` for immediate errors (ERR/CRITICAL).
- [ ] **Verify Data Flow**: Ensure `data/raw/` is populating.
- [ ] **Confirm Dashboard Validation Is Clean**:
    ```powershell
    python -m traderfund.validation.validation_runner --phase dashboard --hook sod_dashboard --market US
    ```

## 4. Handover
- [ ] **Log Entry**: Record "SOD Complete" in daily journal.
