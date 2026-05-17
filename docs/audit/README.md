# Audit Directory Index

## Consolidated Audit Documents

| Document | Covers | Sources Merged |
| :--- | :--- | :--- |
| [FACTOR_REMEDIATION_IMPLEMENTATION_DIGEST.md](FACTOR_REMEDIATION_IMPLEMENTATION_DIGEST.md) | F1 (Temporal Drift), F2 (Regime Partiality), F3 (Narrative Leakage), F5 (Suppression) implementation | 4 files |
| [INDIA_MARKET_AUDIT_CONSOLIDATED.md](INDIA_MARKET_AUDIT_CONSOLIDATED.md) | India parity wiring, data ingestion, IN10Y FRED sourcing, policy/fragility evaluation, delta ingestion | 7 files |
| [TEMPORAL_STATE_AUDIT_CONSOLIDATED.md](TEMPORAL_STATE_AUDIT_CONSOLIDATED.md) | Drift classification, runtime breakage map, post-ignition truth, post-expansion truth, temporal orchestration | 5 files |
| [POLICY_DECISION_WIRING_AUDIT.md](POLICY_DECISION_WIRING_AUDIT.md) | Regime gate, decision policy, fragility engine, dashboard integration | 5 files |
| [DATA_INGESTION_PROXY_AUDIT.md](DATA_INGESTION_PROXY_AUDIT.md) | Load semantics, proxy compliance, US data expansion, ignition execution | 6 files |
| [SCENARIO_TESTING_AND_VERIFICATION.md](SCENARIO_TESTING_AND_VERIFICATION.md) | Factor discontinuity, stress scenarios (S1-S4), Phase 3 hygiene | 3 files |

## System-Wide Audit Snapshots (Chronological)

| Document | Date | Milestone |
| :--- | :--- | :--- |
| [full_system_audit.md](full_system_audit.md) | Jan 29, 2026 | Full stack audit (data → dashboard, capital invariants) |
| [FULL_SYSTEM_AUDIT_POST_INTELLIGENCE.md](FULL_SYSTEM_AUDIT_POST_INTELLIGENCE.md) | Jan 29, 2026 | Post-intelligence layer (safety, execution, capital) |
| [2026-01-24_system_audit.md](2026-01-24_system_audit.md) | Jan 24, 2026 | Freeze v1.1 system boundary audit |
| [inspection_mode_verification_log.md](inspection_mode_verification_log.md) | Feb 9, 2026 | Stress scenario inspection mode testing |

## Runtime Audit Logs (Append-Only)

| Directory | Factor | Contents |
| :--- | :--- | :--- |
| `f1_temporal_drift/` | F1 | drift_breaches.jsonl, evaluation_window_requests.jsonl |
| `f2_regime_partiality/` | F2 | partiality_detections.jsonl, regime_degradations.jsonl |
| `f3_narrative/` | F3 | narrative_suppressions.jsonl, language_violations.jsonl, mode_transitions.jsonl |
| `f5_suppression/` | F5 | suppression_state_snapshots.jsonl, state_transitions.jsonl |

## Temporal Drift Status (JSON snapshots)

- `temporal_drift_status_US.json`
- `temporal_drift_status_INDIA.json`

## Reading Order

For a new reader, the recommended sequence is:
1. **TEMPORAL_STATE** — understand the temporal architecture and system evolution
2. **DATA_INGESTION_PROXY** — understand data sourcing and proxy compliance
3. **INDIA_MARKET** — understand India-specific parity journey
4. **FACTOR_REMEDIATION** — understand F1/F2/F3/F5 governance controls
5. **POLICY_DECISION_WIRING** — understand the decision pipeline
6. **SCENARIO_TESTING** — understand verified robustness
