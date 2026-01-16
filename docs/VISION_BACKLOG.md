# VISION BACKLOG

**Document Type:** Institutional Memory Artifact
**Status:** AWARENESS ONLY — NOT ACTIONABLE
**Last Updated:** 2026-01-17

> [!IMPORTANT]
> This document captures the **full conceptual horizon** of what this system could become over years.
> It is NOT a roadmap. It is NOT an implementation plan. It is a **vision exercise** for awareness and inspiration.

---

## Existing Research & Governance Foundations

This Vision Backlog respects and extends the following authoritative documents:

### Research Module Governance (Summary)
*Source: `docs/governance/RESEARCH_MODULE_GOVERNANCE.md`*

- **Core Philosophy:** Research insight ≠ trading authority. Capital preservation overrides feature velocity.
- **Guardrails:** Physical isolation (`research_modules/`), import barriers, runtime kill-switches.
- **Activation Path:** 30-day observation → 100 paper trades → human sign-off → 90% test coverage.
- **Forbidden Actions:** Auto-optimization, signal overriding, trusting backtests alone.

### Research Product Architecture (Summary)
*Source: `docs/research_product_architecture.md`*

- **Axioms:** Context over calls, uncertainty as a feature, auditable logic, neutral stance.
- **Output Types:** Daily briefs, weekly synthesis, thematic deep dives, cross-market flash alerts.
- **Confidence Semantics:** Signal → Narrative → Report confidence roll-up with decay.
- **Non-Goals:** No portfolio management, no execution, no prediction.

---

## The Three Worlds of This Project

> [!CAUTION]
> These boundaries are non-negotiable. Violation corrupts the entire system.

| World | Purpose | Characteristics |
| :--- | :--- | :--- |
| **Production World** | Live capital operations | Stable, conservative, slow-changing, boring by design |
| **Research World** | Experimental validation | Failure-tolerant, isolated, requires governance passage |
| **Vision World** | Conceptual exploration | Non-actionable, awareness-only, no code, no wiring |

**Critical Rules:**
- Vision items MUST NOT leak into Production.
- Research items MUST pass governance before Production.
- Production remains boring by design.

---

## Vision Axes

The following axes represent the full conceptual space of this project. Each axis contains capabilities that *could exist* in an ideal system, regardless of current feasibility.

---

### Axis 1: Market Intelligence & Information Theory

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Multi-source fusion with credibility weighting | CORE | Mid | ≥5 sources | Bloomberg ≠ Reddit |
| Information velocity detection | RESEARCH | Long | Real-time feeds | How fast is the market learning? |
| Cross-market information propagation modeling | RESEARCH | Long | 6+ months data | US → Asia → Europe spillover lag |
| News lifecycle modeling (birth → saturation → decay) | CORE | Mid | Semantic tags | When is a story "priced in"? |
| Information entropy metrics | PHILOSOPHICAL | Long | Theory | Is the market confused or certain? |
| Synthetic event generation for stress testing | RESEARCH | Mid | Research sandbox | "What if Fed cuts 100bps?" |

---

### Axis 2: Narrative Cognition & Sensemaking

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Narrative contradiction detection | RESEARCH | Mid | Embeddings | Conflicting stories in portfolio |
| Narrative clustering and family trees | CORE | Near | Semantic tags | Related narratives grouped |
| Narrative persistence vs decay theory | CORE | Near | None | When do narratives fade? |
| Narrative fatigue detection | RESEARCH | Mid | 3 months data | Market ignoring repeated themes |
| Counterfactual narrative simulation | RESEARCH | Long | Research sandbox | "What if this narrative hadn't formed?" |
| Narrative confidence bands | CORE | Near | None | Report uncertainty, not point estimates |
| Human-assisted narrative curation | INSTITUTIONAL | Long | Human process | Expert override layer |

---

### Axis 3: Regime & Market State Modeling

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Multi-timeframe regime overlay | RESEARCH | Mid | Daily + Weekly | Short-term vs long-term regime |
| Sector-level regime detection | INSTITUTIONAL | Long | Sector data | Tech regime ≠ Financials regime |
| Regime transition early warnings | CORE | Near | Confidence bands | Falling confidence = transition risk |
| Regime disagreement diagnostics | CORE | Near | None | When VIX and trend disagree |
| Cross-market regime correlation | RESEARCH | Long | Multi-market | US vol → India vol lag |
| Regime impact on narrative weight | CORE | Near | Already wired | Regime dampens narrative conviction |
| Theoretical regime taxonomy expansion | PHILOSOPHICAL | Long | Theory | Beyond the current 8 regimes |

---

### Axis 4: Strategy Selection & Capital Allocation

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Strategy family rotation engines | RESEARCH | Long | Backtests | Momentum → Mean-Reversion timing |
| Gradual re-enable after EVENT_LOCK | CORE | Near | Timer logic | Ramp exposure over 2h |
| Strategy confidence scaling | RESEARCH | Mid | Confidence bands | Lower confidence = smaller size |
| Strategy regret feedback loops | RESEARCH | Long | 6 months trades | Learn from gate decisions |
| Capital allocation optimization (Kelly, etc.) | RESEARCH | Mid | Risk module | Theoretical sizing overlays |
| Portfolio-level strategy coherence | INSTITUTIONAL | Long | Multi-strategy | Strategies must not cancel each other |

---

### Axis 5: Risk, Drawdown & Survival Modeling

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Drawdown prediction from regime | RESEARCH | Long | Historical | "This regime historically causes X% DD" |
| Survival probability dashboards | INSTITUTIONAL | Long | 2+ years data | "Probability of surviving next crash" |
| Maximum drawdown budgeting | CORE | Mid | Risk limits | Pre-commit to worst-case tolerance |
| Stress testing against historical crises | RESEARCH | Mid | Data | Replay 2008, 2020, 2022 |
| Ruin theory integration | PHILOSOPHICAL | Long | Theory | Don't go to zero, ever |
| Dynamic risk budget allocation | INSTITUTIONAL | Long | Capital scale | More capital = different rules |

---

### Axis 6: Human-in-the-Loop Decision Support

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Human override feedback loops | CORE | Mid | UI | Learn from human corrections |
| Expert narrative curation | INSTITUTIONAL | Long | Human process | Analyst-enhanced narratives |
| Decision explanation interfaces | CORE | Near | Explainability | Why did the system do X? |
| Alert fatigue management | CORE | Near | None | Reduce noise, surface only critical |
| Human-machine confidence calibration | RESEARCH | Long | 1 year data | Is human or machine more accurate? |
| Deliberate friction for high-stakes decisions | PHILOSOPHICAL | Long | Culture | Force pause before big moves |

---

### Axis 7: Research, Simulation & Hypothesis Testing

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Research sandboxes isolated from production | CORE | Near | Already exists | `research_modules/` |
| Counterfactual simulation engine | RESEARCH | Long | Synthetic data | "What if X had happened?" |
| A/B testing for narrative rules | RESEARCH | Mid | Paper trading | Compare accumulation rules |
| Hypothesis tracking and validation | CORE | Mid | Logging | Track which ideas worked |
| Automated paper trading harnesses | RESEARCH | Mid | Broker API | Shadow trading for validation |
| Backtest realism enforcement | CORE | Near | Slippage models | No overfitting to history |

---

### Axis 8: System Governance & Safety

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Multi-stage promotion gates | CORE | Near | Already exists | Research → Paper → Prod |
| Automatic rollback on anomaly | CORE | Mid | Monitoring | Bad behavior = instant revert |
| Audit trail for all decisions | CORE | Near | Logging | Complete explainability |
| Change control and versioning | CORE | Near | Already exists | PRs, reviews, sign-offs |
| Emergency kill switches | CORE | Near | Already exists | Halt all trading instantly |
| Regulatory compliance scaffolding | INSTITUTIONAL | Long | Legal | Disclaimers, reporting, record-keeping |

---

### Axis 9: Observability, Explainability & Audit

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Historical Genesis ratios | CORE | Near | 30 days data | Acceptance rate over time |
| Accumulation heatmaps | RESEARCH | Mid | Semantic tags | Visual tag activity |
| Narrative density timelines | CORE | Near | Data | How many narratives active? |
| Regime-narrative correlation views | RESEARCH | Mid | 3 months data | Do regimes predict narrative volume? |
| Complete decision trace ("Glass Box") | CORE | Near | Architecture | Every output traceable to inputs |
| Performance attribution by module | CORE | Mid | PnL tracking | Which module added value? |

---

### Axis 10: Institutional Memory & Learning

| Capability | Nature | Time Horizon | Dependency | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Long-term hypothesis journal | CORE | Near | Documentation | What we believed, when, why |
| Strategy performance archives | CORE | Mid | Data | Historical P/L by strategy |
| Failure post-mortems | CORE | Near | Culture | Learn from mistakes |
| Best practices evolution | CORE | Mid | Documentation | What worked, codified |
| Institutional knowledge graphs | INSTITUTIONAL | Long | Scale | Connect concepts across time |
| Generational knowledge transfer | PHILOSOPHICAL | Long | Culture | System survives personnel changes |

---

## What This Project Will Actively Avoid

> [!CAUTION]
> These are anti-patterns that corrupt the system's integrity.

1.  **Over-automation of judgment** - Machines advise, humans decide.
2.  **Narrative-driven trading without regime** - Context modulates everything.
3.  **Black-box ML decision engines** - Every decision must be explainable.
4.  **Optimizing for backtests over survival** - Backtests lie; survival is truth.
5.  **Feature creep without theory** - Every feature needs a "why" before a "how".
6.  **Trusting single sources** - Multi-source confirmation is mandatory.
7.  **Hiding uncertainty** - Confidence scores are front-and-center.
8.  **Predicting the future** - We characterize the present, not forecast.
9.  **Auto-tuning thresholds** - Constants are frozen for a reason.
10. **Conflating research success with production readiness** - Governance gates exist.

---

## Version History

| Version | Date | Changes |
| :--- | :--- | :--- |
| v1.0 | 2026-01-17 | Initial Vision Backlog creation |
