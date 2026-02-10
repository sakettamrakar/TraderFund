# Shadow Mode

## Shadow Scope

| Phase | Mode | Suppressed Outputs |
| :--- | :--- | :--- |
| Phase 0: Ingestion | live + shadow validation | None (data collection must remain complete). |
| Phase 1: Regime + Narrative | shadow | Externalized transition/advice channels suppressed; outputs tagged `SHADOW`. |
| Phase 2: Meta + Factor | shadow | Trust/permission state is computed but not treated as production authority outside orchestration flow. |
| Phase 3: Strategy + Discovery | shadow | Strategy activation alerts and candidate broadcast outside internal pipeline are suppressed. |
| Phase 4: Convergence | shadow | `HighConvictionIdeas`/`Watchlist` are not emitted as production-facing intelligence; dashboard display only with shadow tagging. |
| Phase 5: Constraints + Portfolio | shadow | Human-operator advisory push channels suppressed; diagnostics remain visible in dashboard shadow view. |
| Phase 6: Dashboard | shadow | All user-facing analytics labeled `SHADOW_MODE`; no recommendation-style escalation. |

## Promotion Criteria

Promotion requires both global shadow exit criteria and phase-specific behavioral criteria from `docs/memory/02_success/success_criteria.md`.

### Global (must pass first)
- [Phase Exit Criteria (Shadow Mode)](../02_success/success_criteria.md#4-phase-exit-criteria-shadow-mode):
  - Stability: zero orphans and zero critical crashes for 2 weeks.
  - Validation: consistent A/B grade signals for 30 days.
  - Idempotency: live and replay outputs match 100% on same data period.
  - Regime robustness across at least 2 distinct regimes.

### Phase-specific gates
- Phase 1 (`Regime Engine`, `Narrative Engine`):
  - [Regime Layer Success](../02_success/success_criteria.md#1-regime-layer-success-l1)
- Phase 3-4 (`Strategy Selector`, L6 lenses, `Convergence Engine`):
  - [Opportunity Discovery Success](../02_success/success_criteria.md#2-opportunity-discovery-success-l6-l7)
- Phase 5 (`Constraint Engine`, `Portfolio Intelligence`):
  - [Portfolio Intelligence Success](../02_success/success_criteria.md#3-portfolio-intelligence-success-l8-l9)
- Phase 6 (`Dashboard (Observer UI)`):
  - [Dashboard & Observability Success](../02_success/success_criteria.md#5-dashboard--observability-success)

## OPEN_QUESTION
- Governance enforcement mode in shadow is not explicitly specified in component contracts: should policy holds be fully active or observation-only during shadow promotion runs.
