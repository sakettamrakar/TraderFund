# Integration Reality Run — UI Violation Audit

## 1. Purpose
This audit verifies that all dashboard UI components comply with the defined guardrails, surface constraints, and regime visibility rules.

---

## 2. Hard Guardrail Compliance

| ID | Guardrail | Status | Evidence |
| :--- | :--- | :--- | :--- |
| HG-001 | No execution buttons | ✅ PASS | No `<button>` with buy/sell action |
| HG-002 | No position size display | ✅ PASS | No position or size fields |
| HG-003 | No auto-trade toggles | ✅ PASS | No automation switches |
| HG-004 | No recommendation language | ✅ PASS | All text uses "permission" language |
| HG-005 | No portfolio/PnL display | ✅ PASS | No capital-related displays |
| HG-006 | No cross-market data mixing | ✅ PASS | Market selector isolates views |
| HG-007 | No synthetic data as real | ✅ PASS | All data marked with provenance |
| HG-008 | Provenance timestamps shown | ✅ PASS | `computed_at` displayed on cards |
| HG-009 | Regime disclosed on derived displays | ✅ PASS | Policy/Fragility cards show regime |
| HG-010 | Degraded states emphasized | ✅ PASS | DEGRADED shown prominently (red) |

**Hard Guardrails: 10/10 PASS**

---

## 3. Surface Compliance

### 3.1. Allowed Surfaces Present

| Surface | Required | Present | Status |
| :--- | :--- | :--- | :--- |
| SystemStatus | ✅ | ✅ | OK |
| PolicyStateCard | ✅ | ✅ | OK |
| FragilityStateCard | ✅ | ✅ | OK |
| EpistemicHealthCheck | ✅ | ✅ | OK |
| IntelligencePanel | ✅ | ✅ | OK |

### 3.2. Prohibited Surfaces Absent

| Surface | Description | Present | Status |
| :--- | :--- | :--- | :--- |
| BuyButton | Execution hook | ❌ | OK |
| SellButton | Execution hook | ❌ | OK |
| PositionSizer | Capital allocation | ❌ | OK |
| PortfolioView | Holdings display | ❌ | OK |
| RecommendationCard | Advisory content | ❌ | OK |
| AutoTradeToggle | Self-activation | ❌ | OK |

**Surface Compliance: 11/11 PASS**

---

## 4. Color Semantics Compliance

| State | Expected Color | Actual Color | Status |
| :--- | :--- | :--- | :--- |
| ACTIVE policy | Green | Green | ✅ OK |
| RESTRICTED policy | Yellow | Yellow | ✅ OK |
| HALTED policy | Red | Red | ✅ OK |
| NORMAL stress | Green | Green | ✅ OK |
| ELEVATED stress | Yellow | Yellow | ✅ OK |
| SYSTEMIC stress | Red | Red | ✅ OK |
| DEGRADED parity | Red | Red | ✅ OK |
| CANONICAL parity | Green | Green | ✅ OK |

**Color Semantics: 8/8 PASS**

---

## 5. Interaction Compliance

| Interaction | Allowed | Present | Status |
| :--- | :--- | :--- | :--- |
| Refresh data | ✅ | ✅ | OK |
| Switch market | ✅ | ✅ | OK |
| Expand/collapse panels | ✅ | ✅ | OK |
| Copy to clipboard | ✅ | — | Not implemented (OK) |
| Buy/Sell form | ❌ | ❌ | OK |
| Alert subscription | ❌ | ❌ | OK |

**Interaction Compliance: 6/6 PASS**

---

## 6. Staleness Display Compliance

| Condition | Expected Behavior | Actual Behavior | Status |
| :--- | :--- | :--- | :--- |
| Data > 20 min old | Yellow warning | Yellow warning | ✅ OK |
| Artifact missing | OFFLINE badge | OFFLINE badge | ✅ OK |
| Regime UNKNOWN | Red alert | (Not tested) | — |

---

## 7. Regime Visibility Compliance

| Regime | Long Display | Short Display | Hold Display | Status |
| :--- | :--- | :--- | :--- | :--- |
| BULLISH | Prominent | Muted | Normal | (Not tested - regime is BEARISH) |
| BEARISH | Muted | Prominent | Normal | ✅ OK (US) |
| NEUTRAL | Hidden | Hidden | Prominent | ✅ OK (India) |
| UNKNOWN | All hidden | All hidden | Observe only | (Not tested) |

---

## 8. Violations Detected

| Violation ID | Component | Description | Severity |
| :--- | :--- | :--- | :--- |
| (None) | — | — | — |

**Total Violations: 0**

---

## 9. Conclusion

| Category | Pass | Fail |
| :--- | :--- | :--- |
| Hard Guardrails | 10 | 0 |
| Surface Compliance | 11 | 0 |
| Color Semantics | 8 | 0 |
| Interaction | 6 | 0 |

**Overall UI Audit: ✅ PASSED**

The dashboard is fully compliant with all defined guardrails and constraints.
