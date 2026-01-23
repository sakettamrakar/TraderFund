---
name: drift-detector
description: A skill to detect and report structural, configuration, or logic discrepancies against defining baselines.
---

# Drift Detector Skill

**Status**: Defined (Phase 2 Unfreeze)
**Authority**: Epistemic Guard (Read-Only)

## 1. Purpose
The Drift Detector is responsible for ensuring the system's actual state matches its intended state (as defined by baselines, hashes, or specifications). It answers the question: "Has this component changed since we last approved it?"

## 2. Core Capabilities

### A. Configuration Drift
*   **Input**: Active `.env` or `config.py` content vs. authoritative `config.example`.
*   **Action**: Compare keys and value types.
*   **Output**: Report of missing keys, type mismatches, or unexpected extra keys.

### B. Structural Drift
*   **Input**: Directory structure vs. `Architecture_Overview.md` (or specific manifest).
*   **Action**: verify existence of required folders and files.
*   **Output**: List of missing critical components or unexpected (rogue) files.

### C. Logic Drift (Future)
*   **Input**: Source code hash vs. `deployment_manifest.json` (signed hash).
*   **Action**: Verify integrity of critical modules (e.g., `regime`, `risk`).
*   **Output**: Pass/Fail on integrity check.

## 3. Operational Constraints

1.  **Read-Only**: This skill **NEVER** modifies files. It does not "fix" drift; it only reports it.
2.  **No Interpretation**: It does not judge whether a change is "good." It only judges if it matches the baseline.
3.  **Deterministic**: Two runs on the same state must produce the exact same report.

## 4. Input Schema

```json
{
  "mode": "structure | config | integrity",
  "target_path": "path/to/check",
  "reference_path": "path/to/baseline (optional)"
}
```

## 5. Output Schema

```json
{
  "status": "DRIFT_DETECTED | SYNCED | ERROR",
  "drift_level": "CRITICAL | WARNING | INFO",
  "differences": [
    {
      "location": "path/key",
      "expected": "value",
      "actual": "value"
    }
  ],
  "timestamp": "ISO8601"
}
```

## 6. Failure Behavior
*   If the baseline is missing: **FAIL** (Cannot verify).
*   If permissions deny read: **FAIL** (Observability Gap).
*   If drift is detected: **SUCCEED** (Job is to report, not fix).

## 7. Relationship to Epistemic Framework
*   **Drift = Epistemic Entropy**.
*   This skill provides the raw data for the **Change Summarizer** or **Audit Log Viewer**.
*   It is the "senses" detecting a violation of the "Freeze."
