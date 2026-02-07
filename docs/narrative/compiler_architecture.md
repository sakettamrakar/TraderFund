# Narrative Compiler Architecture

## 1. Purpose
The **Narrative Compiler** is a deterministic transformation engine that converts structured policy and factor outputs into human-readable explanations.
It is an **epistemic translator**, not an advisor.

---

## 2. Design Principles

### 2.1. Determinism
Given the same input artifacts, the compiler MUST produce the same narrative output.
No randomness, no stochastic phrasing, no LLM creativity.

### 2.2. Transparency
Every sentence must be traceable to a source artifact field.
The narrative does not infer — it reports.

### 2.3. Uncertainty Preservation
Confidence levels, unknown states, and disagreements are surfaced, not hidden.
Low confidence is never smoothed into high confidence language.

### 2.4. Non-Advisory
The narrative describes the system's state, not what the user should do.
It answers "What is?" and "Why?", never "What should I do?".

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      NARRATIVE COMPILER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ Factor      │    │ Regime      │    │ Decision    │         │
│  │ Context     │──▶ │ Context     │──▶ │ Policy      │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                 │                   │                 │
│         ▼                 ▼                   ▼                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              NARRATIVE TEMPLATE ENGINE                   │   │
│  │  1. Select templates by state                           │   │
│  │  2. Fill slots with artifact values                     │   │
│  │  3. Apply regime gating rules                           │   │
│  │  4. Validate against grammar                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              NARRATIVE OUTPUT                            │   │
│  │  • Summary Paragraph                                     │   │
│  │  • Factor Breakdown                                      │   │
│  │  • Policy Statement                                      │   │
│  │  • Fragility Warning (if applicable)                     │   │
│  │  • Provenance Footer                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Input Artifacts

| Artifact | Fields Used |
| :--- | :--- |
| `regime_context_{market}.json` | `regime_code`, `regime_label`, `computed_at` |
| `factor_context_{market}.json` | `factors.*`, `sufficiency`, `regime_input` |
| `decision_policy_{market}.json` | `policy_state`, `permissions`, `blocked_actions`, `reason` |
| `fragility_context_{market}.json` | `stress_state`, `constraints_applied`, `final_authorized_intents`, `reason` |
| `india_parity_status.json` | `parity_status`, `gaps`, `canonical_ready` |

---

## 5. Output Structure

### 5.1. Narrative Sections

1.  **Summary** (1-2 sentences): High-level market state.
2.  **Regime Statement**: Current regime and transition status.
3.  **Factor Breakdown**: State of each factor with confidence.
4.  **Policy Statement**: What is permitted and why.
5.  **Fragility Warning**: Stress state and applied constraints (if any).
6.  **Provenance Footer**: Timestamps and source references.

### 5.2. Example Output

```
## US Market Narrative (2026-01-30)

### Summary
The US market is operating under a BEARISH regime with SYSTEMIC_STRESS detected.
Entry permissions are blocked due to critical volatility.

### Regime
The current regime is **BEARISH**, computed from SPY/QQQ trend analysis.
The market has been in this regime since 2026-01-28.

### Factor States
- **Momentum**: bearish (0.8 confidence)
- **Volatility**: extreme (VIX = 101.58)
- **Liquidity**: neutral (^TNX = 4.2%)
- **Breadth**: tech_lead (QQQ outperforming SPY)

### Policy
Policy state is **RESTRICTED**. The decision layer permits:
- ALLOW_POSITION_HOLD

The following are blocked:
- ALLOW_LONG_ENTRY (Regime BEARISH)
- ALLOW_SHORT_ENTRY (Fragility SYSTEMIC)

Reason: "Regime BEARISH. General Longs discouraged."

### Fragility
Stress state is **SYSTEMIC_STRESS**.
Constraints applied: ALLOW_LONG_ENTRY, ALLOW_SHORT_ENTRY, ALLOW_REBALANCING
Reason: "CRITICAL VOLATILITY (101.58 > 35). Blocking ALL entries."

### Provenance
Regime computed at: 2026-01-30T04:45:00
Policy computed at: 2026-01-30T04:46:00
Fragility computed at: 2026-01-30T04:47:00
```

---

## 6. Template Engine

### 6.1. Template Selection Logic
```python
if stress_state == "SYSTEMIC_STRESS":
    use_template("fragility_critical")
elif policy_state == "HALTED":
    use_template("policy_halted")
elif regime_code == "UNKNOWN":
    use_template("regime_unknown")
else:
    use_template("standard")
```

### 6.2. Slot Filling
Templates contain slots like `{regime_code}`, `{vol_level}`, `{permissions_list}`.
Slots are filled from artifact fields with no transformation.

---

## 7. Validation Pipeline

1.  **Grammar Check**: Is the output using only allowed vocabulary?
2.  **Regime Gate Check**: Does the narrative match the regime context?
3.  **Provenance Check**: Are all cited values traceable to artifacts?
4.  **Hallucination Check**: Is there any text not derivable from inputs?
