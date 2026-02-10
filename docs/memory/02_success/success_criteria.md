# Success Criteria

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This document defines behavioral completion conditions. It answers "When do I trust this system?".

---

## 1. Regime Layer Success (L1)

*Criteria for trusting the "Game We Are Playing" assessment*

- **Stability**: Regime classification remains stable for ≥3 consecutive sessions unless driven by explicit high-impact narrative events.
- **Explainability**: Every regime transition is causally linked to specific factor movements or narrative clusters.
- **Accuracy**: False regime flips (flip-flops within 2 days without price follow-through) occur in < 5% of trading days.
- **Fail-Safe**: System defaults to "Undefined/High Volatility" (cash preservation) when inputs are ambiguous.

## 2. Opportunity Discovery Success (L6-L7)

*Criteria for trusting candidate generation and ranking*

- **Factor Alignment**: ≥60% of High-Conviction Ideas exhibit positive directional alignment with the dominant Factor Regime within 10 trading sessions.
- **Confluence Requirement**: High-Conviction status REQUIRES confirmation from ≥3 independent lenses.
- **Lens Isolation**: Candidates surfaced by a single lens are strictly labeled "Watchlist" or "Low Confidence".
- **Sizing Safety**: No candidate is recommended for entry without a corresponding stop-loss or invalidation level.

## 3. Portfolio Intelligence Success (L8-L9)

*Criteria for trusting risk management and diagnostics*

- **Predictive Diagnostics**: "Regime Conflict" flags appear prior to 80% of major drawdowns (>5%) in historical replay.
- **Narrative Sensitivity**: "Narrative Decay" flags appear within 3 sessions of material negative news events.
- **Horizon Integrity**: All candidates are explicitly labeled with time horizons; operational mismatches (e.g., holding a Scalp for 2 weeks) are flagged immediately.
- **Constraint Hardening**: No position ever exceeds `MAX_POSITION_SIZE` in simulation, regardless of conviction.

## 4. Phase Exit Criteria (Shadow Mode)

*Defines milestones for moving to the next evolutionary phase*

- **Stability**: Zero "Orphans" (data gaps) and zero critical crashes for 2 weeks sustained.
- **Validation**: Consistent generation of "A" or "B" grade signals in Shadow Mode for 30 days.
- **Idempotency**: Live signals match Historical Replay signals 100% for the same data period.
- **Regime Robustness**: Strategy performs predictably (matches expectation) across 2+ distinct market regimes.

*Source: `docs/epistemic/current_phase.md`*

## 5. Dashboard & Observability Success

*Criteria for the "Glass Box" Observer*

- **Latency**: System state updates are visible on Dashboard within 5 seconds of pipeline completion.
- **Traceability**: Every displayed metric links to its source file/lineage.
- **Completeness**: No "Unknown" or "Null" states displayed for active universe symbols; missing data is explicitly flagged as "Stale" or "Insufficient".
- **Alert Visibility**: Critical flags (Red/Orange) utilize distinct visual prominence from standard data headers.

---

## Appendix: Signal Quality Grading

| Grade | Meaning | Criterion |
| :--- | :--- | :--- |
| **A** | High Quality | Validated by T+5 (>2%) AND T+15 (>5%) performance |
| **B** | Acceptable | Validated by T+5 (>1%) OR T+15 (>3%) |
| **C** | Marginal | Flat or slightly negative; inconclusive |
| **D** | Failure | Stop-loss hit or significant adverse excursion |

*Source: `README.md`*
