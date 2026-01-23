# TraderFund Intelligence Platform - Operational Runbook

**Version:** 2.0  
**Last Updated:** 2026-01-14

---

## 1. System Overview

The TraderFund Intelligence Platform is a sophisticated behavioral research system designed to identify and track structural momentum in the US equity markets.

### What it IS:
- A **research-only** system for behavioral market analysis.
- A **multi-layer data lake** that preserves every stage of inference.
- An **autonomous discovery engine** that identifies emerging market narratives.
- A **glass-box platform** where every output is traceable to raw data.

### What it IS NOT:
- **No Trading:** The system cannot place orders or manage capital.
- **No Prediction:** The system identifies current structural setups; it does not predict future prices.
- **No Recommendations:** Outputs are for research validation and audit only.

---

## 2. High-Level Architecture

The system operates as a series of specialized layers, orchestrated by a central scheduler.

### 2.1. Ingestion Layers
- **Layer 1: Metadata Ingestion:** Fetching symbol-level reference data (market cap, industry, sector).
- **Layer 2: Historical backfill:** Budgeted and resumable ingestion of historical data to build context.
- **Layer 3: Incremental Daily Update:** Daily differential fetching of the latest market activity.

### 2.2. Behavioral Analysis Pipeline (6 Stages)
Cycles through behavioral metrics only for symbols that meet prior eligibility criteria:
1.  **Stage 0: Universe Hygiene:** Weekly evaluation of symbol eligibility (volume, listing status).
2.  **Stage 1: Structural Capability:** Assessing the base capacity for a move.
3.  **Stage 2: Energy Setup:** Detecting consolidation and potential energy buildup.
4.  **Stage 3: Participation Trigger:** Identifying early signs of institutional or volume interest.
5.  **Stage 4: Momentum Confirmation:** Validating sustained directional movement.
6.  **Stage 5: Sustainability Risk:** Evaluating the fragility or exhaustion of the move.

### 2.3. Narrative & Research Layers
- **Narrative Evolution:** Tracks the lifecycle of market stories across symbols and time.
- **Narrative Diff Layer:** Specifically identifies what has changed since the last observation.
- **Research Output Layer:** Assembles findings into human-readable daily briefs and logs.

### 2.4. Orchestration Layer
- **Scheduler:** Manages task dependencies and execution timing (Daily vs. Weekly).
- **Activation Controller:** A selective execution gate that ensures only pertinent symbols consume computation/API budgets.

---

## 3. Daily Execution Flow (Primary)

The system is designed to run autonomously following market close.

### Trigger
Triggered by the system scheduler (or manual CLI invocation).

### Task Sequence
1.  **Incremental Update:** Fetches data for symbols in the active universe (respecting API budgets).
2.  **Pipeline Activation:** The `PipelineController` evaluates which symbols have new data and which analysis stages should be triggered.
3.  **Analysis Execution:** Eligible symbols are processed through the 6-stage pipeline.
4.  **Narrative Evolution:** The output of analysis is clustered and used to update the state of market narratives.
5.  **Narrative Diff:** The system identifies key delta changes (e.g., a narrative moving from "Emerging" to "Confirmed").
6.  **Research Output:** Generation of the Daily Research Brief and validation snapshots.

### Expected Outputs
- Updated `data/research_reports/` files.
- Research validation logs in `data/validation/research_log.csv`.
- Persistent state updates in the Narrative Graph.

### Normal "No-Op" Behavior
It is normal for the daily run to result in "No-Op" for many symbols. If no symbol meets the activation threshold for a stage, the system will record a quiet day. **Silence is a sign of high signal-to-noise filtering, not failure.**

---

## 4. Weekly Execution Flow

Conducted once per week (typically on weekends) for maintenance and structural updates.

### Maintenance Tasks
1.  **Universe Hygiene (Stage 0):** Full refresh of eligible symbols based on the expanded universe (≈500-650 symbols).
2.  **Historical Backfill:** The system identifies gaps in historical data and uses the remaining weekly API budget to fill them.
3.  **Structural Refresh:** Updating reference metadata (Metadata Ingestion).
4.  **Weekly Research Summary:** Aggregation of the week's narrative drifts and structural shifts.

---

## 5. Manual Operations

While the system is autonomous, manual intervention is supported for diagnostics.

### 5.1. Dry Runs
To see what the scheduler plans to do without executing API calls or writing data:
```powershell
python -m orchestration.runner --mode daily --dry-run
python -m orchestration.runner --mode weekly --dry-run
```

### 5.2. Debug Stage Execution
To force a specific symbol through the pipeline controller for debugging:
```powershell
python -m research_modules.pipeline_controller.runner --run --symbols SYMBOL_NAME
```

### 5.3. Safe Re-execution
The system is idempotent. Re-running a daily task will generally detect existing data and perform a "No-Op" unless specifically forced.

---

## 6. Configuration & Controls

### 6.1. API Budgets
- Controls are located in `ingestion/config.py` and specific runner configs.
- **Incremental Budget:** Typically 50 symbols per day.
- **Backfill Budget:** Typically 50-100 symbols per week.

### 6.2. Selective Activation
Controlled by `research_modules.pipeline_controller.config`. This prevents "symbol sprawl" where thousands of low-quality symbols consume resources.

### 6.3. Kill Switches
Located in `infra_hardening.control.switches.SystemSwitches`.
- `READ_ONLY_MODE`: Instantly stops all disk writes.
- `SANDBOX_ENABLED`: Disables the strategy sandbox layer.

---

---

## 7. Automated Scheduling & API Scaling

### 7.1. API Key Pool Management
The system now uses an **API Key Pool** (`ApiKeyManager`) to scale capacity beyond single-key limits.
- **Configuration:** Add keys to `.env` as a comma-separated list.
  ```env
  ALPHA_VANTAGE_KEYS=key1,key2,key3
  ALPHA_VANTAGE_API_KEY=legacy_fallback_key
  ```
- **Quotas:** Keys are rotated automatically when daily safety limits are reached (default: 450 calls/key).
- **Global Limit:** A hard global limit (50 calls/day) is enforced regardless of key capacity to prevent runaway costs/usage.

### 7.2. Windows Task Scheduler Setup
To enable autonomous execution, register the provided Windows Tasks.

**New Task Types (Phase 3):**
- **Narrative Engine**: Runs daily at 16:15 IST (Market Close + 45m). Command: `python bin/run_narrative.py`
- **Decision Engine**: Runs daily at 16:30 IST. Command: `python bin/run_decision.py`

**Register Tasks:**
```powershell
# Registers both Daily (18:30) and Weekly (Sat 10:00) tasks
python -m infra_hardening.scheduler.manage --register
```

**Manage Tasks:**
```powershell
# Check status
python -m infra_hardening.scheduler.manage --query

# Force manual run via Wrapper (ensures logging)
python infra_hardening/scheduler/wrapper.py --mode daily
```

**Logs:**
Scheduler logs are written to: `logs/scheduler/` (timestamped).

---

## 8. Failure Handling & Recovery

### What happens on task failure?
- The Orchestration Engine catches exceptions and logs a `FAILURE` state for that task.
- Subsequent dependent tasks are skipped.
- The system continues to the next independent task branch (Graceful Degradation).

### How to safely resume?
- Simply re-run the scheduler. The `incremental_update` and `backfill` modules track their own state and will pick up where they left off.
- The `PipelineController` tracks last-run timestamps for every (symbol, stage) pair in `data/master/us/execution_history.parquet`.

### What NOT to do:
- **Do NOT** manually delete files in `data/staging/` or `data/master/` unless performing a full reset.
- **Do NOT** bypass the scheduler for bulk ingestion (to avoid API rate limiting).

---

## 8. Common Misconceptions (IMPORTANT)

- **"Why is the system silent on a 10% mover?"**
  A symbol moving 10% does not automatically qualify for research. It must meet the **Structural Capability** (Stage 1) and **Energy Setup** (Stage 2) criteria *before* the move to be considered systematic.
- **"Why are some symbols stuck in Stage 1?"**
  Symbols are not "forced" through the pipeline. They must EARN their way to Stage 4 (Momentum Confirmation). If a symbol lacks the necessary structural setup, it will stay in Stage 1 indefinitely.
- **"Is the system broken if daily brief is empty?"**
  No. High-quality research requires patience. On quiet market days, an empty brief is the correct output, signifying no high-probability structural shifts were detected.

---

**System Integrity Contact:** Research Audit Team  
**Documentation:** `docs/Architecture_Overview.md` | `docs/IMPLEMENTATION_STATUS.md`
