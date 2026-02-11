# Failure Model

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This document describes failure scenarios, retry behaviors, degradation paths, and fallback behaviors across all system layers.
> Intent only. No implementation.

---

## 1. Design Approach

The system is designed to **fail closed** — when in doubt, do nothing. Uncertainty is amplified, not smoothed. Gaps are declared, not filled. The core invariant is:

> **Staleness over Fabrication. Silence over Hallucination. Halt over Guess.**

| Principle | Description |
| :--- | :--- |
| **Fail Closed** | Unknown state → block all action, not permit default action |
| **No Silent Degradation** | Every component must flag `INSUFFICIENT_DATA` rather than silently produce reduced-quality output |
| **Monotonic Suppression** | Downstream layers may only subtract permissions, never add them |
| **Human Recovery** | All governance-level failures require operator intervention — no auto-recovery |
| **Audit Everything** | Every failure, skip, retry, and degradation is logged with full context |

*(Sources: `docs/memory/04_architecture/macro.md`, `docs/epistemic/bounded_automation_contract.md`)*

---

## 2. Temporal Failures

### 2.1 Temporal Drift States

| Failure | Condition | Severity | Detection | Response |
| :--- | :--- | :--- | :--- | :--- |
| **Ingestion Drift** | `RDT >> CTT` | WARNING | Temporal orchestrator | Operator alert, investigate data source lag |
| **Evaluation Pending** | `CTT >> TE` | WARNING | Dashboard staleness indicator | Block new decisions until evaluation runs |
| **Future Leakage** | `TE > CTT` | **CRITICAL** | Invariant check (`TE ≤ CTT ≤ RDT`) | Immediate system halt, manual audit required |
| **Cross-Market Divergence** | `abs(TE_US - TE_INDIA) > 1 Day` | WARNING | Global synchronization gate | Warn operator; allow independent operation unless explicit dependency |
| **RDT Undetermined** | Cannot compute Raw Data Time | HIGH | Temporal orchestrator | Log failure, CTT cannot advance, TE frozen |

### 2.2 Temporal Recovery

| Recovery Action | Authority | Mechanism |
| :--- | :--- | :--- |
| Advance TE after drift resolution | Operator | Intelligence Gate passage (all checks pass) |
| Manual TE override (emergency) | Operator (Admin) | CLI with explicit confirmation flag + audit log justification |
| Rollback TE | Operator (Admin) | CLI with justification + Decision Ledger entry |

*(Sources: `docs/governance/truth_advancement_gates.md`, `docs/irr/failure_log.md` TDR-001/TDR-002/TDR-003)*

---

## 3. Ingestion Layer Failures (L0)

### 3.1 US Market (Alpha Vantage — REST/Batch)

| Failure | Detection | Retry Policy | Fallback | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **API rate limited (HTTP 429)** | Response status code | Exponential backoff; rotate to next API key | Defer symbol to retry queue | LOW |
| **API key exhaustion** | All keys exhausted in pool | Wait until daily reset | Log, defer entire batch | MEDIUM |
| **Symbol not found** | API returns empty/error | Log to retry queue, skip symbol | Remove from active universe after 3 consecutive failures | LOW |
| **Empty response / no data** | Empty payload | No retry (not transient) | Log warning, do NOT overwrite existing data | MEDIUM |
| **Symbol refresh returns 0** | `LISTING_STATUS` returns empty | No retry | Alert operator; retain previous symbol master | HIGH |
| **Daily fetch fails > 10% universe** | Batch completion check | Retry failed batch | Alert operator; CTT does NOT advance | HIGH |
| **Schema validation failure** | Column/type mismatch | No retry (data issue) | Reject data; CTT does NOT advance | HIGH |
| **Network timeout** | `ConnectionError` / `Timeout` | 3 retries with backoff | Check internet, check vendor status | MEDIUM |
| **Price drift > circuit breaker** | Drift check in Ingestion Gate | No retry | Manual review required before CTT advance | HIGH |

### 3.2 India Market (SmartAPI — WebSocket/Streaming)

| Failure | Detection | Retry Policy | Fallback | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **WebSocket disconnect** | Connection lost event | Auto-reconnect with exponential backoff | REST fallback available | MEDIUM |
| **Binary parse error** | Tick decode failure | Skip tick, log anomaly | Continue with remaining ticks | LOW |
| **Authentication failure** | Login/token error | Re-authenticate (token refresh) | Alert operator if persistent | HIGH |
| **Instrument master stale** | Cache age > 24h | Re-download on next startup | Use cached version with WARNING | MEDIUM |
| **Tick gap (missing symbols)** | Health check detects no ticks for symbol | No retry (market-driven) | Log gap, flag symbol as STALE | MEDIUM |
| **Duplicate ticks on restart** | Restart recovery overlap | No retry needed | Downstream dedup by `(symbol, timestamp)` | LOW |

### 3.3 Ingestion Restart Behavior

| Scenario | Behavior | Safety |
| :--- | :--- | :--- |
| **Scheduler restart** | Re-authenticates, re-loads instrument master, resumes polling | Safe — append-only raw storage |
| **Duplicate run** | Concurrent writes produce duplicate records in raw JSONL | Intentional — raw layer (Bronze) is append-only; dedup at Silver |
| **Market-closed run** | Scheduler logs "Outside market hours. Sleeping..." and idles | Safe — checks time every 60 seconds |
| **Outside-hours flag** | Bypasses market hours check, fetches data | Safe — enables testing and manual recovery |

*(Sources: `docs/verification/ingestion_failure_modes.md`, `docs/us_market_engine_design.md`, `docs/INDIA_WEBSOCKET_ARCHITECTURE.md`)*

---

## 4. Regime Layer Failures (L1)

| Failure | Detection | Degradation Path | Response |
| :--- | :--- | :--- | :--- |
| **Partial canonical data** | Symbol availability check | Regime degrades to `UNKNOWN` / low confidence | Fail closed — all downstream blocked |
| **Missing blocking symbol** | Regime input contract check | `NOT_VIABLE` — regime computation FORBIDDEN | System halt for regime-dependent layers |
| **Insufficient history** | Lookback window check (< 756 days) | `NOT_VIABLE` | Block regime; retain previous state with STALE flag |
| **Temporal misalignment** | Intersection check across symbols | Excluded from computation | Regime computed on reduced symbol set (with confidence penalty) |
| **Conflicting indicators** | VIX vs trend disagreement | `TRANSITION_UNCERTAIN` classification | Block new entries, wait for confirmation |
| **Regime flapping** | State changes > N within lookback | Cooldown lock active | Suppress transitions until cooldown expires |
| **Stale data** | Data age > MAX_STALENESS | False stability risk | Mark regime as STALE; dashboard shows warning |
| **Data quality violation** | Forward-fill, interpolation, synthetic data detected | `NOT_VIABLE` | Regime computation FORBIDDEN |

**Regime Ingestion Obligations** (all must be satisfied for regime computation):

| Obligation | Description | Failure = |
| :--- | :--- | :--- |
| `OBL-RG-ING-SYMBOLS` | All contract symbols ingested | Regime FORBIDDEN |
| `OBL-RG-ING-HISTORY` | ≥ 756 trading days per symbol | Regime FORBIDDEN |
| `OBL-RG-ING-ALIGNMENT` | Temporal intersection ≥ 756 days | Symbol excluded |
| `OBL-RG-ING-QUALITY` | No forward-fill, no interpolation, no synthetic | Regime FORBIDDEN |
| `OBL-RG-ING-ENFORCEMENT` | All above SATISFIED | Regime FORBIDDEN if ANY unmet |

**Silent Fallback is FORBIDDEN**: If regime runs on incomplete data, that is a `GOVERNANCE VIOLATION`.

*(Sources: `docs/memory/05_components/regime_engine.yaml`, `docs/epistemic/governance/regime_ingestion_obligations.md`, `docs/epistemic/contracts/minimal_regime_input_contract.md`)*

---

## 5. Narrative Layer Failures (L2)

| Failure | Detection | Degradation Path | Response |
| :--- | :--- | :--- | :--- |
| **Missing artifact** | Required input not found | Section omitted with explicit message | `"[Section] could not be generated. Artifact missing: {path}."` |
| **Parse error** | Artifact cannot be decoded | Section omitted with explicit message | `"[Section] could not be generated. Data format error in {path}."` |
| **Regime UNKNOWN** | Regime state unresolved | Limited narrative (stasis only) | `"Narrative generation is limited. Regime could not be determined."` |
| **Stale data** | Data beyond staleness threshold | Staleness warning prepended | `"Warning: Data may be stale. Last computed: {timestamp}."` |
| **Compiler failure** | Cannot produce valid output | Fallback narrative emitted | `"Narrative generation failed. Reason: {reason}. Manual inspection recommended."` |
| **Event source unavailable** | News API / RSS down | Narratives STALE | Log, retain previous narratives with staleness flag |

**Hallucination Controls** (preventing false output):

| Control | Description |
| :--- | :--- |
| Source Binding | Every sentence must cite its input artifact field |
| No Interpolation | No inferred values, no trend extrapolation, no gap-filling |
| No Creative Phrasing | Fixed templates only — no synonyms, no paraphrasing |
| Uncertainty Amplification | Low confidence → amplified uncertainty language, not smoothed |
| Pre-Emission Validation | Grammar, source binding, regime compatibility, prohibited word scan |
| No Partial Emission | If compiler fails, emit fallback — never emit partial or guessed narrative |

*(Sources: `docs/narrative/failure_and_hallucination_controls.md`, `docs/memory/05_components/narrative_engine.yaml`)*

---

## 6. Factor & Meta-Analysis Failures (L3–L4)

### 6.1 Factor Engine (L4)

| Failure | Detection | Degradation Path | Response |
| :--- | :--- | :--- | :--- |
| **Insufficient data for computation** | Lookback check | Degrade to `UNKNOWN` | Flag as `INSUFFICIENT_DATA`; downstream receives explicit null |
| **Factor state UNKNOWN** | Computation yields indeterminate result | Lens degrades to `INSUFFICIENT_DATA` | No silent default — explicitly declared |
| **Proxy data missing** | Benchmark/growth proxy unavailable | Use reduced proxy set (if benchmark available) | Log; if benchmark missing → `UNAVAILABLE` |
| **Cross-market binding error** | Wrong market context loaded | Fail closed | Log anomaly; e.g., "No benchmark binding for US" when processing India |

### 6.2 Factor Lens (L4 → L6)

| Failure | Detection | Degradation Path | Response |
| :--- | :--- | :--- | :--- |
| **Factor state unavailable** | Input check | Lens returns `INSUFFICIENT_DATA` | Downstream receives explicit null, not a guess |
| **Insufficient sector coverage** | Coverage check | Relative comparison impossible | Flag limitation in output |
| **Cross-market pattern data missing** | Lead-lag data unavailable | Cross-market alerts suppressed | Log; single-market analysis continues |

### 6.3 Fundamental Lens (L6)

| Failure | Detection | Degradation Path | Response |
| :--- | :--- | :--- | :--- |
| **Data source unavailable** | API check | Returns `INSUFFICIENT_DATA` | No silent degradation (governance rule) |
| **Stale financial data** | Data age > reporting period | Flag as `STALE` | Downstream informed of data age |
| **Insufficient sector coverage** | Coverage check | Relative comparison impossible | Flag limitation |

### 6.4 Meta Engine (L3)

| Failure | Detection | Degradation Path | Response |
| :--- | :--- | :--- | :--- |
| **All signals stale** | Staleness detection (beyond horizon) | Trust scores decayed to zero | No actionable output; explicit "all stale" flag |
| **Conflicting signal sources** | Conflict detection | Conflict flagged with attribution | Both sides preserved in output; operator decides |
| **Empty input** | No signals received | No meta-analysis produced | Clean exit logged |

*(Sources: `docs/memory/05_components/factor_engine.yaml`, `docs/memory/05_components/factor_lens.yaml`, `docs/memory/05_components/fundamental_lens.yaml`, `docs/memory/05_components/meta_engine.yaml`)*

---

## 7. Strategy & Convergence Failures (L5–L7)

### 7.1 Strategy Selector (L5)

| Failure | Detection | Degradation Path | Response |
| :--- | :--- | :--- | :--- |
| **No strategies eligible** | All filtered by regime/factor gates | Empty activation set | Clean exit — "No strategies compatible with current regime" |
| **Staleness threshold exceeded** | Belief freshness check | Strategy auto-suspended | Suspended until beliefs refresh |
| **Registry corruption** | Schema validation failure | Strategy rejected at load | Log, skip strategy, continue with remainder |

### 7.2 Convergence Engine (L7)

| Failure | Detection | Degradation Path | Response |
| :--- | :--- | :--- | :--- |
| **Regime state unavailable** | Input check | Degrade to equal-weight scoring | Flag as `INSUFFICIENT_DATA` |
| **Single lens dominance** | Weight check | Constrained scoring | Flag imbalance in output |
| **Zero candidates** | All candidates filtered | No convergence output | Clean exit logged |

*(Sources: `docs/memory/05_components/strategy_selector.yaml`, `docs/memory/05_components/convergence_engine.yaml`)*

---

## 8. Execution Harness Failures

### 8.1 State Validation Failures

| Condition | Harness Behavior | Recovery |
| :--- | :--- | :--- |
| `regime_state` is None | **HALT** — Cannot execute without regime | Operator must run regime pipeline |
| `regime_state.confidence < MIN_THRESHOLD` | **DEGRADE** — Execute with reduced scope | Log warning; narrower task graph |
| `factor_permission` is None (not implemented) | **ASSUME PERMISSIVE** — Log bypass | Continue with warning |
| `beliefs` is empty | **SKIP** — Nothing to execute | Clean exit logged |
| Any state older than `MAX_STALENESS` | **REJECT** — Refuse to execute | Operator must refresh data |

### 8.2 Task Graph Failures

| Failure Type | Policy | Impact |
| :--- | :--- | :--- |
| Single non-critical task fails | Mark task `FAILED`, continue independent tasks | Partial cycle completion |
| Critical-path task fails | Mark entire cycle `DEGRADED` | Log prominently; dependent tasks skipped |
| Circular dependency detected | **REJECT** at graph construction | Cycle does not start |
| Harness-level error | **HALT** — Stop all execution | Require human intervention |
| Timeout exceeded | Terminate task, mark `FAILED` | Continue with remaining tasks |

### 8.3 Skill Violations

| Violation | Response | Escalation |
| :--- | :--- | :--- |
| Undeclared output (side effect) | Quarantine skill, halt cycle | `SKILL_VIOLATION` audit event |
| Permission bypass attempt | Reject execution, log violation | Continue cycle |
| Layer bypass detected | Quarantine skill, log violation | Require review |
| Repeated violations (≥ 3) | Permanent skill deregistration | Decision Ledger entry required |

*(Source: `docs/contracts/execution_harness_contract.md`)*

---

## 9. Circuit Breakers & Policy Failures

### 9.1 Decision Policy (Governance Gate)

The Decision Policy asks: **"Is the system allowed to consider action?"**

| Condition | Policy Output | Effect |
| :--- | :--- | :--- |
| `ProxyStatus == DEGRADED` | `OBSERVE_ONLY` | All action blocked — "Epistemic Foundation Insufficient" |
| `Regime == UNCERTAIN` | `OBSERVE_ONLY` | No transactional actions |
| `Regime == BEARISH` | `ALLOW_SHORT_ENTRY` or `OBSERVE_ONLY` | Long entries blocked |
| `Liquidity == TIGHT/CRISIS` | Block `LONG_ENTRY`, `SHORT_ENTRY` | Position hold only (tighter stops) |
| `Breadth == DIVERGENT` | `ALLOW_LONG_ENTRY (Conditional)` | High-quality only restriction |

### 9.2 Fragility Policy (Systemic Circuit Breaker)

The Fragility Policy asks: **"Is the environment safe?"** It has **subtractive power only** — can revoke permissions, never grant.

| Stress State | Revoked Permissions | Trigger Signals |
| :--- | :--- | :--- |
| **NORMAL** | None | All signals nominal |
| **EVALUATING** | `BLOCK_NEW_ENTRY` | Insufficient data (startup) |
| **ELEVATED_STRESS** | `BLOCK_LEVERAGE`, `BLOCK_AGGRESSIVE_ENTRY` | VIX spike, rate spike, volume evaporation |
| **SYSTEMIC_STRESS** | `BLOCK_ALL_ENTRIES`, `FORCE_DEFENSIVE_HOLD` | Multiple signals firing, critical liquidity shock |
| **TRANSITION_UNCERTAIN** | `BLOCK_ALL_ENTRIES` | Recent regime flip (< 5 days) |

**Permission Final Formula**: `Final = DecisionPolicy.Permissions − FragilityPolicy.Revocations`

**Market Scope**:
- **US**: Full fragility evaluation enabled
- **India**: Hard-coded `NOT_EVALUATED` (Reason: `DEGRADED_PROXY`) — handled by Decision Policy `OBSERVE_ONLY`

### 9.3 EVENT_LOCK

| Trigger | Effect | Duration | Recovery |
| :--- | :--- | :--- | :--- |
| Extreme volatility event | Temporary halt of all new entries | Until event subsides | Explicit operator re-enable |

*(Sources: `docs/contracts/decision_policy_contract.md`, `docs/contracts/fragility_policy_contract.md`)*

---

## 10. Degraded State Registry

Degraded states are explicitly declared, documented, and scoped. The system may operate in degraded mode only with full transparency.

### 10.1 Active Degraded States

| ID | Market | Description | Substitution | Epistemic Risk | Authorized Phase |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DEG-IN-001** | India | Missing broad index (NIFTY50, BANKNIFTY) | `NSE_RELIANCE` as single-stock surrogate | Idiosyncratic risk conflated with systemic risk | Phase 10–11 only |
| **DEG-US-001** | US | Missing Small Cap (IWM), Industrials (DIA) | None (SPY + QQQ only) | Blindness to small-cap rotation and breadth divergences | All phases (acceptable approximation) |

### 10.2 Degraded State Handling Rules

| Condition | UI Effect | Confidence Effect | Strategy Effect |
| :--- | :--- | :--- | :--- |
| `Status == DEGRADED` | "⚠️ PROXY LIMITED" badge | Confidence capped at `MEDIUM` (0.5) | Tighter constraints (higher margin of safety) |
| `Status == CANONICAL (with warnings)` | Secondary warning | No cap | Unchanged |

### 10.3 Surrogate Authorization

| Market | Index | Authorized Surrogate | Label Requirement |
| :--- | :--- | :--- | :--- |
| India | NIFTY | `NSE_RELIANCE` | Must display as "SURROGATE" in UI |
| India | BANKNIFTY | `NSE_HDFCBANK` | Must display as "SURROGATE" in UI |
| India | CNXIT | `NSE_INFY` | Must display as "SURROGATE" in UI |

*(Sources: `docs/data/degraded_state_registry.md`, `docs/data/data_source_governance.md`)*

---

## 11. Dashboard & UI Failures

| Failure | Detection | Fallback | User-Facing Message |
| :--- | :--- | :--- | :--- |
| **Backend unavailable** | API connection failure | Show last known state, grey out all derived displays | "Unable to connect to data layer. Showing last known state." |
| **Artifact missing** | 404 on policy/context endpoint | Show OFFLINE badge | "Policy artifact not found. System OFFLINE." |
| **Parse error** | JSON decode error | Show generic error card | "Data format error. Contact system administrator." |
| **Stale data** | Staleness threshold exceeded | Grey out affected panels | "STALE (Xm since last update) — DO NOT TRUST REGIME" |
| **Epoch divergence** | Multiple TE sources disagree | Surface both with conflict indicator | "Temporal truth source inconsistency detected." |
| **Synthetic displayed as real** | Invariant violation (`HG-007`) | Immediate rollback | Never display synthetic data as real |

**Dashboard Hard Guardrails** (inviolable):

| Guardrail | Description |
| :--- | :--- |
| No execution buttons | `INV-NO-EXECUTION` |
| No position size display | `INV-NO-CAPITAL` |
| No auto-trade toggles | `INV-NO-SELF-ACTIVATION` |
| No recommendation language | Observatory principle |
| No portfolio value / PnL | No capital implication |
| Degraded states MORE visible | `OBL-HONEST-STAGNATION` |

*(Sources: `docs/dashboard/ui_guardrails.md`, `docs/dashboard/stress_inspection_mode_spec.md`)*

---

## 12. Shadow Mode Failures

| Failure | Detection | Response | Severity |
| :--- | :--- | :--- | :--- |
| **Governance Leakage** | Shadow run emits action strings (e.g., "BUY") in weak/unknown context | Log as `GOVERNANCE_LEAKAGE`; does not affect real systems | HIGH (epistemic) |
| **Honest Stagnation** | Shadow run executes under `Unknown` regime | Expected behavior — system correctly refuses | LOW (informational) |
| **Temporal Drift carry-over** | Shadow run inherits drifted TE from IRR environment | Log; no temporal closure in shadow | MEDIUM |
| **Schema mismatch** | Core policy reads `regime` field, tick context writes `regime_code` | Resolves to `UNKNOWN` / `HALTED` | HIGH |
| **Cross-market binding leakage** | India processing references US benchmark bindings | Log anomaly; should not cross | HIGH |

**Shadow Safety Verification** (mandatory after every shadow run):
1. No real execution was performed
2. No broker endpoint was called
3. No capital state file was modified
4. All action outputs went to `ShadowExecutionSink` only

*(Sources: `docs/irr/shadow_reality_run_log.md`, `docs/irr/failure_log.md`)*

---

## 13. IRR Failure Taxonomy (Observed)

Integration Reality Runs (IRR) have revealed five canonical failure classes:

| Class | Name | Description | Phase-7 Gate |
| :--- | :--- | :--- | :--- |
| **F1** | Temporal Drift Accumulation | Unbounded `CTT > TE` drift weakens trust in evaluated reality | **P0 BLOCKER** |
| **F2** | Regime Instability Under Partial Updates | Same-day produces path-dependent regime truth | **P0 BLOCKER** |
| **F3** | Narrative Over-Resolution in Stagnation | Action-like outputs in stagnation imply unjustified decisiveness | **P2 CONDITIONAL** |
| **F4** | UI Epistemic Leakage | Dashboard surfaces conflicting epoch references | **P0 BLOCKER** |
| **F5** | Suppression Dominance Opacity | Cannot distinguish intentional suppression from pipeline breakage | **P1 BLOCKER** |

**Remediation Priority**:

| Priority | Classes | Rationale |
| :--- | :--- | :--- |
| **P0** | F1, F2, F4 | Core truth-time integrity, deterministic regime, UI truth disclosure |
| **P1** | F5 | Suppression explainability for operator trust |
| **P2** | F3 | Narrative conservatism after foundational stabilization |

**Required before any controlled Truth Advancement**: All P0 classes resolved and verified.

*(Source: `docs/governance/irr_failure_remediation_map.md`)*

---

## 14. Epistemic Drift Detection

The system tracks six classes of epistemic drift — structural or conceptual changes that may silently corrupt system integrity:

| Drift Class | Definition | Detection | Severity |
| :--- | :--- | :--- | :--- |
| **Ontological** | New concepts introduced without declaration | Concept registry validation | WARNING / FAIL |
| **Causal** | Layers acting as causes instead of constraints | Dependency direction audit | FAIL |
| **Boundary** | Layer assuming responsibilities of another layer | Responsibility matrix check | FAIL |
| **Permission** | Signals/execution bypassing policy layers | Permission chain validation | **CRITICAL** |
| **Temporal** | Fast layers mutating slow beliefs | Temporal integrity audit | FAIL |
| **Latent → Active** | Latent layers silently activated without authorization | Activation declaration check | **CRITICAL** |

**Drift Severity Levels**:

| Level | Meaning | Action |
| :--- | :--- | :--- |
| INFO | Minor discrepancy | Log only |
| WARNING | Potential drift, review recommended | Log + flag for review |
| FAIL | Confirmed drift | Block deployment + require resolution |
| **CRITICAL** | Safety violation | Immediate halt + Decision Ledger entry required |

*(Source: `docs/contracts/epistemic_drift_validator_specification.md`)*

---

## 15. Component Failure Summary (All Layers)

| Component | Layer | Key Failure | Degradation Response |
| :--- | :--- | :--- | :--- |
| **Ingestion US** | L0 | API rate limit, empty data | Retry queue, defer; do NOT overwrite |
| **Ingestion India** | L0 | WebSocket disconnect, parse error | Auto-reconnect; skip bad ticks |
| **Ingestion Events** | L0 | Source unavailable, stale events | Log; narratives stale |
| **Regime Engine** | L1 | Partial data, conflicting indicators | `UNKNOWN` / `NOT_VIABLE` |
| **Narrative Engine** | L2 | Missing artifact, regime unknown | Fallback narrative or limited stasis output |
| **Meta Engine** | L3 | All signals stale | Trust scores decayed to zero |
| **Factor Engine** | L4 | Insufficient data | `UNKNOWN`; explicit null downstream |
| **Factor Lens** | L4→L6 | Factor state unavailable | `INSUFFICIENT_DATA` |
| **Fundamental Lens** | L6 | Data source unavailable | `INSUFFICIENT_DATA` (no silent degradation) |
| **Technical Lens** | L6 | Insufficient candle history | Indicator unavailable; flag gap |
| **Momentum Engine** | Scanner | Insufficient history, late candles | Stale signals flagged |
| **Strategy Selector** | L5 | No eligible strategies | Empty activation set (clean exit) |
| **Convergence Engine** | L7 | Regime unavailable | Equal-weight fallback, flagged `INSUFFICIENT_DATA` |
| **Portfolio Intelligence** | L9 | Regime stale | All items flagged as potentially misaligned |
| **Governance** | Cross | Obligation index stale | All obligations marked `UNKNOWN` |
| **Dashboard** | UI | Backend unavailable, stale data | Last known state + grey out + staleness warning |

---

## 16. Troubleshooting Quick Reference

| Symptom | Likely Cause | First Action |
| :--- | :--- | :--- |
| `ConnectionError` / `Timeout` in logs | API connectivity | Check internet → check vendor status → restart ingestion |
| Raw events incoming, no narratives | Pipeline blockage | Check `run_narrative.py` logs → verify vector store → check freeze flag |
| Narratives exist, no decisions | Decision gap | Check `run_decision.py` logs → verify confidence > 0.8 → check constraint validator |
| JSON decode errors / invalid timestamps | Data corruption | Isolate corrupt file to `data/quarantine/` → run constraint validator → document in evolution log |
| Dashboard shows STALE | Data not updating | Check if market is open → check runner logs → do not rely on stale regime |
| Regime stuck at UNKNOWN | Partial canonical data | Check regime input contract symbols → verify history depth → run ingestion |

*(Source: `docs/runbooks/troubleshooting.md`)*

---

## Legacy Source Mapping

| Section | Legacy Source Document(s) |
| :--- | :--- |
| §2 Temporal | `docs/governance/truth_advancement_gates.md`, `docs/irr/failure_log.md` |
| §3 Ingestion | `docs/verification/ingestion_failure_modes.md`, `docs/us_market_engine_design.md`, `docs/INDIA_WEBSOCKET_ARCHITECTURE.md` |
| §4 Regime | `docs/memory/05_components/regime_engine.yaml`, `docs/epistemic/governance/regime_ingestion_obligations.md` |
| §5 Narrative | `docs/narrative/failure_and_hallucination_controls.md` |
| §6 Factor/Meta | Component YAMLs (factor_engine, factor_lens, fundamental_lens, meta_engine) |
| §7 Strategy/Convergence | Component YAMLs (strategy_selector, convergence_engine) |
| §8 Harness | `docs/contracts/execution_harness_contract.md` |
| §9 Circuit Breakers | `docs/contracts/decision_policy_contract.md`, `docs/contracts/fragility_policy_contract.md` |
| §10 Degraded States | `docs/data/degraded_state_registry.md`, `docs/data/data_source_governance.md` |
| §11 Dashboard | `docs/dashboard/ui_guardrails.md`, `docs/dashboard/stress_inspection_mode_spec.md` |
| §12 Shadow | `docs/irr/shadow_reality_run_log.md`, `docs/irr/failure_log.md` |
| §13 IRR Taxonomy | `docs/governance/irr_failure_remediation_map.md` |
| §14 Drift | `docs/contracts/epistemic_drift_validator_specification.md` |
| §16 Troubleshooting | `docs/runbooks/troubleshooting.md` |
