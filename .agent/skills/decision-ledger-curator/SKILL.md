---
name: Decision Ledger Curator
description: Structural skill to maintain the integrity and chronological order of the Decision Ledger.
version: 1.0.0
---

# Decision Ledger Curator

**Purpose**: To enforce the Append-Only nature of `decisions.md` and ensure a standardized schema. This prevents "Cowboy Decisions" (undocumented or malformed entries).

## 1. Capabilities

### 1.1. Create Decision
*   **Action**: Append a new entry to `docs/epistemic/ledger/decisions.md`.
*   **Inputs**: Title, Decision Summary, Rationale, Impacted Documents.
*   **Logic**:
    1. Read last ID (e.g., D008).
    2. Increment ID (D009).
    3. Format Date (YYYY-MM-DD).
    4. Append formatted markdown block.

## 2. Usage

### Command Line
```powershell
python bin/run-skill.py decision-ledger-curator --title "Authorize New Algo" --decision "Allow Algo X to run" --rationale "Backtest passed" --impact "algo_x.py" --user curator_bot
```
