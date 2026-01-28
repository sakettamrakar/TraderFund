# Dashboard Data Wiring

This document maps API endpoints to their source-of-truth artifacts in the `Evolution` plane.

**Strict Rule**: The dashboard **never computes** new signal values. It only **reads** what `EV-TICK` has already produced.

## Wiring Map

| API Endpoint | Source Artifact(s) | Logic |
| :--- | :--- | :--- |
| `GET /system/status` | `docs/epistemic/ledger/evolution_log.md` <br> `docs/evolution/ticks/{latest}/` | Read latest tick timestamp. Parse latest log entry for errors. Check expansion/dispersion JSONs for activity state. |
| `GET /layers/health` | `docs/evolution/ticks/{latest}/*.json` <br> `docs/evolution/meta_analysis/*.md` | Check `os.stat().st_mtime` of critical artifacts. If > 24h old (or > tick interval), mark STALE. |
| `GET /market/snapshot` | `docs/evolution/ticks/{latest}/factor_context.json` <br> `docs/evolution/ticks/{latest}/*_watcher.json` | JSON Load & Extract strict fields (`state`, `confidence`). |
| `GET /watchers/timeline` | `docs/evolution/ticks/tick_*/` | Iterate last N directories sorted by timestamp. Extract states. |
| `GET /strategies/eligibility` | `docs/evolution/ticks/{latest}/factor_context.json` | In-memory comparison of Context vs. Static Strategy Rules (e.g. `Momentum needs Bull Vol`). **NO EXECUTION**. |
| `GET /meta/summary` | `docs/evolution/meta_analysis/evolution_comparative_summary.md` | Read file content. Regex parse sections if structured, or return raw markdown. |
| `GET /system/activation_conditions` | **Hardcoded / Config** | Static strings defining the epistemic safeguards. |

## Failure Handling

*   **Missing Artifact**: Return `HTTP 200` with `status: "ERROR" / "UNKNOWN"` in JSON body. Do not crash.
*   **Corrupt JSON**: Log error to stderr, return empty/safe default structure.
*   **No Ticks**: Return "System initializing..." state.
