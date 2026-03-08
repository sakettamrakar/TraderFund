# Retry Policy

Derived from `failure_modes` in `docs/memory/05_components/*.yaml`.

| Component | retryable | max_attempts | backoff | fail_behavior | Source YAML Version |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Governance` | yes | 3 | exponential (5s, 10s, 20s) | Enter `Lockdown Mode` (read-only, no updates) if ledger remains unavailable. | 2026-02-23 |
| `Data Ingestion (US)` | yes | 6 | exponential with jitter (5s..60s) | Reject update and keep prior valid snapshot (`T-1`) on persistent API/schema failure. | 2026-02-23 |
| `Data Ingestion (India)` | yes | 5 | exponential (1s, 2s, 4s, 8s, 16s) | Mark feed degraded and continue with explicit gap/latency telemetry. | 2026-02-23 |
| `Event Ingestion` | yes | 4 | exponential (2s, 4s, 8s, 16s) | Halt new event intake; downstream must surface stale external-context state. | 2026-02-23 |
| `Regime Engine` | yes | 2 | linear (10s, 10s) | Emit `UNKNOWN`/`INSUFFICIENT_DATA`; default to conservative posture (`Risk-Off`). | 2026-02-23 |
| `Narrative Engine` | yes | 2 | linear (15s, 15s) | Emit stale/unweighted narratives when dependencies fail; no causal invention. | 2026-02-23 |
| `Meta-Analysis Engine` | no | 0 | n/a | Fail-closed to lowest reliability score when required history is missing. | 2026-02-23 |
| `Factor Engine` | yes | 2 | exponential (5s, 10s) | Emit `INSUFFICIENT_DATA`; deny permissions by default (fail-closed). | 2026-02-23 |
| `Strategy Selector` | no | 0 | n/a | Auto-suspend on staleness/regime incompatibility; await human authorization backlog resolution. | 2026-02-23 |
| `Momentum Engine` | yes | 3 | exponential (1s, 2s, 4s) | Suppress invalid momentum outputs and expose NaN/clock-skew diagnostics. | 2026-02-23 |
| `Narrative Lens` | no | 0 | n/a | Emit empty candidate pool or low-confidence mapping diagnostics. | 2026-02-23 |
| `Factor Lens` | yes | 2 | exponential (5s, 10s) | Emit zero candidates when permissions/data quality remain invalid. | 2026-02-23 |
| `Fundamental Lens` | no | 0 | n/a | Return `INSUFFICIENT_DATA` until fundamental ingestion wiring (RC-4) is active. | 2026-02-23 |
| `Technical Lens` | no | 0 | n/a | Reset indicators on gap/insufficient lookback and suppress affected setups. | 2026-02-23 |
| `Strategy Lens` | no | 0 | n/a | Skip dependency-failed or inactive strategies; emit no candidate for skipped branches. | 2026-02-23 |
| `Convergence Engine` | no | 0 | n/a | Emit empty output/watchlist-only state; never invent candidates. | 2026-02-23 |
| `Constraint Engine` | yes | 2 | exponential (5s, 10s) | Fail-closed (`Block All`) when portfolio/risk state cannot be fetched. | 2026-02-23 |
| `Portfolio Intelligence` | no | 0 | n/a | Emit `STALE/AMBIGUOUS` diagnostics and degraded advisory output. | 2026-02-23 |
| `Dashboard (Observer UI)` | yes | 5 | exponential with jitter (1s..30s) | Show explicit `DISCONNECTED`/stale state; remain read-only. | 2026-02-23 |

## Unresolved Implementation Gaps

- `ACTION ITEM` [Target Resolution: Integration Team]: `Narrative Engine` includes `Regime adapter NOT_WIRED` in failure modes. Retries cannot resolve this structural integration gap; the adapter requires explicit implementation wiring to satisfy the regime requirement contract.
