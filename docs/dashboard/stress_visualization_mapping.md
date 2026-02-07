# Stress Visualization Mapping
**Purpose:** Defines the data transformation rules from the Audit Report to Dashboard Widgets.

---

## S1: Volatility Shock
**Source:** Audit Log (S1 Section)

| Source Field (Markdown) | Dashboard Widget | Target Prop / Field | Transformation Logic |
| :--- | :--- | :--- | :--- |
| `Condition: VIX > 35` | **MarketSnapshot** | `snapshot.volatility` | Display "CRITICAL (Simonulated 40.0)" |
| `Result Stress State: SYSTEMIC_STRESS` | **SystemPosture** | `posture.stress_state` | Map directly. Color: RED. |
| `Constraints: [...]` | **FragilityStateCard** | `constraints_applied` | List display of revoked permissions. |
| `VERDICT` | **SystemStatus** | `banner` | "STRESS TEST PASS: Action Suppressed" |

## S2: Liquidity Tightening
**Source:** Audit Log (S2 Section)

| Source Field | Dashboard Widget | Target Prop | Transformation |
| :--- | :--- | :--- | :--- |
| `Condition: Liquidity = TIGHT` | **MarketSnapshot** | `snapshot.liquidity` | Display "TIGHT (Simulated)" |
| `Policy State: RESTRICTED` | **PolicyStateCard** | `policy_decision.state` | Map to "RESTRICTED". Color: AMBER. |
| `Blocked Actions` | **PolicyStateCard** | `policy_decision.blocks` | List display of blocked actions. |
| `VERDICT` | **WhyNothingIsHappening** | `blockers` | Inject "Liquidity Gate: FAILED (Simulated)" |

## S3: Regime Instability
**Source:** Audit Log (S3 Section)

| Source Field | Dashboard Widget | Target Prop | Transformation |
| :--- | :--- | :--- | :--- |
| `Condition: Regime = UNKNOWN` | **MarketSnapshot** | `snapshot.regime` | Display "UNKNOWN (Simulated)" |
| `Policy State: HALTED` | **SystemStatus** | `system_status` | "HALTED" |
| `Policy State: HALTED` | **PolicyStateCard** | `policy_decision.state` | Map to "HALTED". Color: GREY/RED. |
| `Permissions: ['OBSERVE_ONLY']` | **PolicyStateCard** | `permissions` | Verify ONLY "OBSERVE_ONLY" is present. |

## S4: Data Degradation (Logical)
**Source:** Audit Log (S4 Section)

| Source Field | Dashboard Widget | Target Prop | Transformation |
| :--- | :--- | :--- | :--- |
| `Condition: Data Insufficiency` | **DataAnchorPanel** | `sufficiency` | Force one layer to "INSUFFICIENT" (Simulated). |
| `Result: ...collapses to Regime Instability` | **SystemStatus** | `alert_banner` | "DATA INTEGRITY FAIL -> SYSTEM HALT" |
| `VERDICT` | **DataAnchorPanel** | `confidence_level` | Force to "NONE" / "HALTED". |

---

## Global Decoration Rules (All Scenarios)

1. **Watermark**: All widgets must inherit a `data-mode="inspection"` attribute.
2. **Epoch Override**: Display `Epoch: SIM-TE-2026-01-30`.
3. **Disclaimers**:
   - Bottom of every card: *"visualization only - not live"*
   - Top Filter: *"Viewing Scenario: S[x]"*
