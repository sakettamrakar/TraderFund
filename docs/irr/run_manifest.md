# Integration Reality Run — Manifest

## 1. Run Identification
| Field | Value |
| :--- | :--- |
| **Run ID** | `IRR-2026-01-30-001` |
| **Execution Mode** | `DRY_RUN` (Design Phase) |
| **Truth Epoch** | `TE-2026-01-30` |
| **Data Mode** | `REAL_ONLY` |
| **Markets** | US, INDIA |
| **Timestamp** | 2026-01-30T05:35:00+05:30 |

---

## 2. Purpose
The Integration Reality Run (IRR) validates that all governance layers function correctly under real-world data conditions.
The goal is to **surface failures and edge cases**, not to generate trading insights.

---

## 3. Scope

### 3.1. Layers Under Test
| Layer | Component | Test Focus |
| :--- | :--- | :--- |
| DATA | Market Loader, Parity Checker | Data availability, freshness, provenance |
| FACTOR | Factor Context Builder | Computation correctness, sufficiency |
| REGIME | Regime Context Builder | Regime detection, transition handling |
| INTELLIGENCE | Decision Policy Engine | Permission logic, gate enforcement |
| FRAGILITY | Fragility Policy Engine | Stress detection, subtraction logic |
| DASHBOARD | All UI Components | Truth alignment, surface compliance |
| NARRATIVE | Narrative Compiler | Grammar compliance, hallucination prevention |

### 3.2. Markets Under Test
| Market | Parity Status | Expected Behavior |
| :--- | :--- | :--- |
| US | CANONICAL | Full evaluation, all layers active |
| INDIA | CANONICAL | Full evaluation, all layers active |

---

## 4. Input Artifacts

| Artifact | Path | Status |
| :--- | :--- | :--- |
| US Regime Context | `docs/evolution/context/regime_context_US.json` | Verified |
| US Factor Context | `docs/evolution/context/factor_context_US.json` | Verified |
| US Decision Policy | `docs/intelligence/decision_policy_US.json` | Verified |
| US Fragility Context | `docs/intelligence/fragility_context_US.json` | Verified |
| India Regime Context | `docs/evolution/context/regime_context_INDIA.json` | Verified |
| India Factor Context | `docs/evolution/context/factor_context_INDIA.json` | Verified |
| India Decision Policy | `docs/intelligence/decision_policy_INDIA.json` | Verified |
| India Fragility Context | `docs/intelligence/fragility_context_INDIA.json` | Verified |
| India Parity Status | `docs/intelligence/india_parity_status.json` | Verified |

---

## 5. Expected Outputs

| Output | Path | Description |
| :--- | :--- | :--- |
| Failure Log | `docs/irr/failure_log.md` | All failures encountered |
| Suppression Events | `docs/irr/suppression_events.md` | Signals/actions suppressed |
| Regime Instability | `docs/irr/regime_instability_report.md` | Regime edge cases |
| Narrative Failures | `docs/irr/narrative_failure_matrix.md` | Grammar/hallucination violations |
| UI Violations | `docs/irr/ui_violation_audit.md` | Dashboard guardrail violations |

---

## 6. Success Criteria

| Criterion | Threshold |
| :--- | :--- |
| Zero mock data present | 0 synthetic values |
| All artifacts have provenance | 100% traceability |
| All regime gates explicit | 100% regime disclosure |
| No execution hooks present | 0 action buttons |
| No recommendation language | 0 violations |
| Staleness properly displayed | 100% compliance |

---

## 7. Run Sequence

1.  **Data Validation**: Verify all market data is real and non-stale.
2.  **Factor Computation**: Run factor context builders for both markets.
3.  **Regime Computation**: Run regime context builders for both markets.
4.  **Policy Evaluation**: Run decision policy engines for both markets.
5.  **Fragility Evaluation**: Run fragility policy engines for both markets.
6.  **Dashboard Verification**: Audit all dashboard surfaces for compliance.
7.  **Narrative Generation**: Generate narratives and validate against grammar.
8.  **Failure Collection**: Aggregate all failures, suppressions, and violations.
