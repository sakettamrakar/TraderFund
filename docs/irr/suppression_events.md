# Integration Reality Run — Suppression Events

## 1. Purpose
This document logs all signals, permissions, or actions that were **suppressed** by governance layers.
Suppression is a safety feature, not a failure.

---

## 2. Suppression Sources

| Layer | Suppression Type |
| :--- | :--- |
| Decision Policy | Permission denial |
| Fragility Policy | Permission subtraction |
| Regime Gate | Signal invalidation |
| Parity Check | Market lockout |

---

## 3. US Market Suppression Events

### 3.1. Decision Policy Suppressions

| Event ID | Suppressed Permission | Reason | Computed At |
| :--- | :--- | :--- | :--- |
| `SUP-US-D-001` | ALLOW_LONG_ENTRY | Regime BEARISH | 2026-01-30 04:46 |
| `SUP-US-D-002` | ALLOW_LONG_ENTRY_SPECIAL | Regime does not favor longs | 2026-01-30 04:46 |

### 3.2. Fragility Policy Suppressions

| Event ID | Suppressed Permission | Reason | Computed At |
| :--- | :--- | :--- | :--- |
| `SUP-US-F-001` | ALLOW_LONG_ENTRY | SYSTEMIC_STRESS (VIX > 35) | 2026-01-30 04:50 |
| `SUP-US-F-002` | ALLOW_SHORT_ENTRY | SYSTEMIC_STRESS (VIX > 35) | 2026-01-30 04:50 |
| `SUP-US-F-003` | ALLOW_LONG_ENTRY_SPECIAL | SYSTEMIC_STRESS | 2026-01-30 04:50 |
| `SUP-US-F-004` | ALLOW_REBALANCING | SYSTEMIC_STRESS | 2026-01-30 04:50 |

### 3.3. Net Effect (US)

| Permission | Decision Grants? | Fragility Allows? | Final Status |
| :--- | :--- | :--- | :--- |
| ALLOW_LONG_ENTRY | ❌ | ❌ | BLOCKED |
| ALLOW_SHORT_ENTRY | ✅ | ❌ | BLOCKED |
| ALLOW_LONG_ENTRY_SPECIAL | ✅ | ❌ | BLOCKED |
| ALLOW_POSITION_HOLD | ✅ | ✅ | **ALLOWED** |
| ALLOW_REBALANCING | — | ❌ | BLOCKED |

**Final US Authorized**: `ALLOW_POSITION_HOLD` only.

---

## 4. India Market Suppression Events

### 4.1. Decision Policy Suppressions

| Event ID | Suppressed Permission | Reason | Computed At |
| :--- | :--- | :--- | :--- |
| `SUP-IND-D-001` | ALLOW_LONG_ENTRY | Regime NEUTRAL | 2026-01-30 05:23 |
| `SUP-IND-D-002` | ALLOW_SHORT_ENTRY | Regime NEUTRAL | 2026-01-30 05:23 |

### 4.2. Fragility Policy Suppressions

| Event ID | Suppressed Permission | Reason | Computed At |
| :--- | :--- | :--- | :--- |
| (None) | — | Stress state NORMAL | 2026-01-30 05:23 |

### 4.3. Net Effect (India)

| Permission | Decision Grants? | Fragility Allows? | Final Status |
| :--- | :--- | :--- | :--- |
| ALLOW_LONG_ENTRY | ❌ | ✅ | BLOCKED (Decision) |
| ALLOW_SHORT_ENTRY | ❌ | ✅ | BLOCKED (Decision) |
| ALLOW_POSITION_HOLD | ✅ | ✅ | **ALLOWED** |
| ALLOW_REBALANCING | ✅ | ✅ | **ALLOWED** |

**Final India Authorized**: `ALLOW_POSITION_HOLD`, `ALLOW_REBALANCING`.

---

## 5. Suppression Summary

| Market | Suppressions by Decision | Suppressions by Fragility | Final Permissions |
| :--- | :--- | :--- | :--- |
| US | 2 | 4 | 1 |
| India | 2 | 0 | 2 |

---

## 6. Suppression Integrity Check

**Invariant**: Suppression is monotonic. Once suppressed, a permission cannot be restored by a downstream layer.

| Check | Result |
| :--- | :--- |
| Decision → Fragility monotonicity | ✅ PASSED |
| Fragility never grants | ✅ PASSED |
| Final ⊆ Decision permissions | ✅ PASSED |
