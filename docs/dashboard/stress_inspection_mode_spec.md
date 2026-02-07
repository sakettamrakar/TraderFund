# Stress Inspection Mode Specification
**Version:** 1.0.0
**Epoch:** TE-2026-01-30
**Intent:** Safe, ephemeral visualization of stress degradation mechanics.

---

## 1. Architectural Overview

The Stress Inspection Mode is a **read-only, ephemeral visualization layer** that parses static audit logs to simulate dashboard states. It operates entirely on the Frontend/Backend API layer without interacting with the Intelligence Engine or creating any persistent artifacts.

### 1.1 Core Principles
1.  **Source of Truth**: `docs/audit/phase_3_stress_scenario_report.md` (and related logs) ONLY. No live calculation.
2.  **Ephemerality**: No data is stored or cached beyond the request lifecycle.
3.  **Isolation**: Live dashboard bindings must NEVER be touched. Inspection uses a dedicated "Shadow Store" in the frontend.
4.  **Disclosure**: Every component must show "INSPECTION MODE: TE-2026-01-30" badges.

## 2. Backend Design

### 2.1 Loader: `StressReportLoader`
A new loader (`dashbaord/backend/loaders/inspection.py`) responsible for parsing the Markdown report into a structured JSON schema.

**Input**: `docs/audit/phase_3_stress_scenario_report.md`

**Parser Logic:**
- Identify Sections `## S[x]`.
- Extract `Condition` string.
- Extract Market Blocks (`### INDIA`, `### US`).
- Parse Key-Value pairs (`- Key: Value` or `- List: [A, B]`).
- Extract Verdicts.

### 2.2 API Endpoint
**GET** `/api/inspection/stress_scenarios`

**Response Schema:**
```json
{
  "trace": {
    "source": "docs/audit/phase_3_stress_scenario_report.md",
    "epoch": "TE-2026-01-30",
    "mode": "DRY_RUN_VISUALIZATION"
  },
  "scenarios": [
    {
      "id": "S1",
      "name": "Volatility Shock",
      "condition_desc": "VIX > 35 (Critical Stress)",
      "markets": {
        "INDIA": {
          "inputs": { "VIX": 40.0 },
          "outcomes": {
             "stress_state": "SYSTEMIC_STRESS",
             "constraints": ["ALLOW_LONG_ENTRY", "ALLOW_REBALANCING", "ALLOW_SHORT_ENTRY"]
          },
          "verdict": "PASS (Action Suppressed)"
        }
      }
    }
  ]
}
```

## 3. Frontend Design

### 3.1 Inspection Mode Activation
- **Trigger**: A "Stress Lab" or "Inspection" button in the footer (Debug/Admin area).
- **Behavior**: Opens a Modal or Full-Screen Overlay.
- **State**: `isInspectionMode = true`.

### 3.2 Visual Components
The Inspection View will leverage existing Dumb Components but wrap them in a **StressAdaptor**.

**StressAdaptor Component:**
- **Props**: `scenarioData`, `market`.
- **Function**:
    - Converts `scenarioData.outcomes` into the specific shapers required by `SystemPosture`, `PolicyStateCard`, etc.
    - Forces visual "Stress Testing" styling (e.g., striped backgrounds, "SIMULATION" watermarks).

### 3.3 Scenario Selector
- A sidebar or tab list allowing the user to toggle between `S1`, `S2`, `S3`, `S4`.
- Selecting a scenario updates the "Virtual Dashboard" to reflect the parsed state.

## 4. Safety Constraints (Invariants)

| Invariant | Implementation Mechanism |
| :--- | :--- |
| **INV-NO-EXECUTION** | Inspection Mode has NO bindings to Execution Gate or Strategy runners. |
| **INV-NO-PERSISTENCE** | Parser is strictly Read-Only. No 'Save' or 'Export' actions. |
| **INV-SEPARATION** | Uses distinct API namespace (`/api/inspection/*`). Live endpoints blocked in Inspection. |
| **INV-DISCLOSURE** | UI must flash "NON-LIVE TRUTH" or "SCENARIO VISUALIZATION" prominently. |

## 5. Exit Criteria & Reversion
- Closing the Inspection Modal destroys the `scenarioData` in Frontend state.
- Dashboard automatically re-fetches canonical `/api/system/status` to confirm return to Live Truth.
