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

## 3. Reporting
- [ ] **Generate Summary**:
    ```powershell
    python bin/run-skill.py --skill change-summarizer --diff-range "today"
    ```
- [ ] **Log Entry**: Record "EOD Complete" in daily journal. 
