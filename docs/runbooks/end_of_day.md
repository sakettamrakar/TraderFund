# End of Day (EOD) Runbook

**Trigger**: 15:45 IST (Market Close + 15m)
**Owner**: Operator (Human)

## 1. Process Termination
- [ ] **Stop Ingestion**: Gracefully terminate ingestion scripts (Ctrl+C).
- [ ] **Stop Runners**: Gracefully terminate momentum/logic scripts.

## 2. Data Validation
- [ ] **Check Orphan Count**: How many events failed processing?
    ```powershell
    # Manual check of logs or future skill output
    ```
- [ ] **Verify Decision Artifacts**:
    ```powershell
    # Check data/decisions/ for today's output
    ls data/decisions/US/$(date +%Y-%m-%d)
    ```
- [ ] **Archive**: Ensure daily data is preserved.
- [ ] **Run Post-Close Validation Sweep**:
    ```powershell
    foreach ($phase in 'ingestion','memory','research','evaluation','dashboard') {
        python -m traderfund.validation.validation_runner --phase $phase --hook eod_check --market US
        if ($LASTEXITCODE -ne 0) { break }
    }
    ```

- [ ] **If A Phase Fails, Attempt Safe Phase-Local Remediation**:
    ```powershell
    python -m traderfund.validation.validation_runner --phase <phase> --hook eod_remediate --market US --auto-remediate
    python -m traderfund.validation.validation_runner --phase <phase> --hook eod_verify --market US
    ```
    Replace `<phase>` with one of `ingestion`, `memory`, `research`, `evaluation`, or `dashboard`.

## 3. Reporting
- [ ] **Generate Summary**:
    ```powershell
    python bin/run-skill.py --skill change-summarizer --diff-range "today"
    ```
- [ ] **Review Validation Summaries**:
    Check `logs/validation/` and capture any material issue in the relevant verification report.
- [ ] **Log Entry**: Record "EOD Complete" in daily journal. 
