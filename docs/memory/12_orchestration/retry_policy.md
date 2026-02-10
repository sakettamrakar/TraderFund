# Retry Policy

Derived from `failure_modes` in `docs/memory/05_components/*.yaml`.

| Component | retryable | max_attempts | backoff | fail_behavior |
| :--- | :--- | :--- | :--- | :--- |
| `Governance` | yes | 3 | exponential (5s, 10s, 20s) | Enter `Lockdown Mode` (read-only, no updates) if ledger remains unavailable. |
| `Data Ingestion (US)` | yes | 6 | exponential with jitter (5s..60s) | Reject update and keep prior valid snapshot (`T-1`) on persistent API/schema failure. |
| `Data Ingestion (India)` | yes | 5 | exponential (1s, 2s, 4s, 8s, 16s) | Mark feed degraded and continue with explicit gap/latency telemetry. |
| `Event Ingestion` | yes | 4 | exponential (2s, 4s, 8s, 16s) | Halt new event intake; downstream must surface stale external-context state. |
| `Regime Engine` | yes | 2 | linear (10s, 10s) | Emit `UNKNOWN`/`INSUFFICIENT_DATA`; default to conservative posture (`Risk-Off`). |
| `Narrative Engine` | yes | 2 | linear (15s, 15s) | Emit stale/unweighted narratives when dependencies fail; no causal invention. |
| `Meta-Analysis Engine` | no | 0 | n/a | Fail-closed to lowest reliability score when required history is missing. |
| `Factor Engine` | yes | 2 | exponential (5s, 10s) | Emit `INSUFFICIENT_DATA`; deny permissions by default (fail-closed). |
| `Strategy Selector` | no | 0 | n/a | Auto-suspend on staleness/regime incompatibility; await human authorization backlog resolution. |
| `Momentum Engine` | yes | 3 | exponential (1s, 2s, 4s) | Suppress invalid momentum outputs and expose NaN/clock-skew diagnostics. |
| `Narrative Lens` | no | 0 | n/a | Emit empty candidate pool or low-confidence mapping diagnostics. |
| `Factor Lens` | yes | 2 | exponential (5s, 10s) | Emit zero candidates when permissions/data quality remain invalid. |
| `Fundamental Lens` | no | 0 | n/a | Return `INSUFFICIENT_DATA` until fundamental ingestion wiring (RC-4) is active. |
| `Technical Lens` | no | 0 | n/a | Reset indicators on gap/insufficient lookback and suppress affected setups. |
| `Strategy Lens` | no | 0 | n/a | Skip dependency-failed or inactive strategies; emit no candidate for skipped branches. |
| `Convergence Engine` | no | 0 | n/a | Emit empty output/watchlist-only state; never invent candidates. |
| `Constraint Engine` | yes | 2 | exponential (5s, 10s) | Fail-closed (`Block All`) when portfolio/risk state cannot be fetched. |
| `Portfolio Intelligence` | no | 0 | n/a | Emit `STALE/AMBIGUOUS` diagnostics and degraded advisory output. |
| `Dashboard (Observer UI)` | yes | 5 | exponential with jitter (1s..30s) | Show explicit `DISCONNECTED`/stale state; remain read-only. |

## OPEN_QUESTION
- `Narrative Engine` includes `Regime adapter NOT_WIRED` in failure modes. Retries cannot resolve this structural integration gap; policy above only covers transient dependency failures.
