# Success Criteria

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This document defines behavioral completion conditions. It answers "When do I trust this system?".

---

## 1. Regime Layer Success (L1)

*Criteria for trusting the "Game We Are Playing" assessment*

🔹 **Invariant 1.1 — Regime Stability**
Regime classification MUST remain stable for ≥3 consecutive sessions unless driven by explicit high-impact narrative events.

🔹 **Invariant 1.2 — Explainability**
Every regime transition MUST be causally linked to specific factor movements or narrative clusters.

🔹 **Invariant 1.3 — Accuracy**
False regime flips (flip-flops within 2 days without price follow-through) MUST occur in < 5% of trading days.

🔹 **Invariant 1.4 — Fail-Safe**
System MUST default to "Undefined/High Volatility" (cash preservation) when inputs are ambiguous.

## 2. Opportunity Discovery Success (L6-L7)

*Criteria for trusting candidate generation and ranking*

🔹 **Invariant 2.1 — Factor Alignment**
≥60% of High-Conviction Ideas MUST exhibit positive directional alignment with the dominant Factor Regime within 10 trading sessions.

🔹 **Invariant 2.2 — Confluence Requirement**
High-Conviction status REQUIRES confirmation from ≥3 independent lenses.

🔹 **Invariant 2.3 — Lens Isolation**
Candidates surfaced by a single lens MUST be strictly labeled "Watchlist" or "Low Confidence".

🔹 **Invariant 2.4 — Sizing Safety**
No candidate MUST be recommended for entry without a corresponding stop-loss or invalidation level.

🔹 **Invariant 2.5 — Score Dispersion**
High-Conviction Ideas MUST exhibit minimum variance ≥ 0.24 across candidates. Flat distributions are invalid.

## 3. Portfolio Intelligence Success (L8-L9)

*Criteria for trusting risk management and diagnostics*

🔹 **Invariant 3.1 — Predictive Diagnostics**
"Regime Conflict" flags MUST appear prior to 80% of major drawdowns (>5%) in historical replay.

🔹 **Invariant 3.2 — Narrative Sensitivity**
"Narrative Decay" flags MUST appear within 3 sessions of material negative news events.

🔹 **Invariant 3.3 — Horizon Integrity**
All candidates MUST be explicitly labeled with time horizons; operational mismatches (e.g., holding a Scalp for 2 weeks) MUST be flagged immediately.

🔹 **Invariant 3.4 — Constraint Hardening**
No position MUST ever exceed `MAX_POSITION_SIZE` in simulation, regardless of conviction.

## 4. Phase Exit Criteria (Shadow Mode)

*Defines milestones for moving to the next evolutionary phase (enforced via `docs/governance/truth_advancement_gates.md`)*

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
*Note: Testing implementations and test-specific invariants belong in the tests/ directory or a separate testing contract.*

## 6. Convergence Computation Observability (L7)

- **Latency Logging**: All convergence scores must log computation latency.

## 7. L3 — Meta-Analysis Success
<!-- Invariant 01: L3 Meta-Analysis Logic -->
Invariant 01 — Regime Dependency

Meta-Analysis MUST consume the current RegimeState (L1).

If RegimeState is undefined:

trust_score = 0.0
status = "INSUFFICIENT_CONTEXT"

Meta-Analysis MUST NOT execute without L1 context.

Purpose: Prevent level skipping.

Invariant 2 — Trust Score Boundaries

Every trust score MUST:

Be within [0.0, 1.0]

Be deterministic for identical inputs

If trust_score < 0.0 or > 1.0 → HARD FAILURE.

Purpose: Prevent unstable scoring drift.

🔹 Invariant 3 — Regime-Aware Trust Adjustment

Trust logic MUST adapt to regime state:

In CHOP or TRANSITION regime:

Technical breakout trust ≤ 0.50

In TRENDING regime:

Momentum trust ≥ 0.60 IF factor alignment present

Violations MUST be rejected during semantic validation.

Purpose: Encode "don't trust breakouts in chop."

🔹 Invariant 4 — Explainability Requirement

Each trust decision MUST log:

Signal type

Regime context

Adjustment reason

Final trust score

Computation latency (ms)

Silent trust calculations are forbidden.

Purpose: Enforce glass-box observability.


