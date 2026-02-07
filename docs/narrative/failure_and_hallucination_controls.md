# Narrative Failure and Hallucination Controls

## 1. Purpose
This document defines the controls that prevent the Narrative Compiler from producing **hallucinated**, **misleading**, or **unverifiable** output.
The narrative must never claim more than the data supports.

---

## 2. Definition of Hallucination

A **hallucination** is any narrative statement that:
1.  Cannot be derived from input artifacts.
2.  Implies information not present in the data.
3.  Contradicts the input artifacts.
4.  Invents values, states, or relationships.

---

## 3. Hallucination Prevention Controls

### 3.1. Source Binding
Every sentence must cite its source artifact.

| Sentence | Required Source |
| :--- | :--- |
| "Regime is BEARISH." | `regime_context.regime_code` |
| "VIX is 25.4." | `factor_context.factors.volatility.level` |
| "Long entry is blocked." | `decision_policy.blocked_actions` |

**Implementation**: The compiler maintains a `source_map` that links each output sentence to its input field.

### 3.2. No Interpolation
The compiler MUST NOT:
*   Infer values from patterns ("VIX was 20 yesterday and 25 today, so it's rising").
*   Extrapolate trends ("This suggests continued volatility").
*   Fill in missing data ("Likely around 7%").

If a value is missing, emit: `"{field} could not be determined."`

### 3.3. No Creative Phrasing
The compiler uses **fixed templates** only.
No synonym substitution, no paraphrasing, no stylistic variation.

**Correct**: "Volatility level: 25.4, classified as elevated."
**Hallucination**: "Volatility is quite high and may cause concern."

### 3.4. Uncertainty Amplification
When confidence is low, the narrative MUST amplify uncertainty, not smooth it.

| Confidence | Phrasing |
| :--- | :--- |
| > 0.8 | "High confidence assessment." |
| 0.5 - 0.8 | "Moderate confidence. Exercise caution." |
| < 0.5 | "Low confidence. Assessment may be unreliable." |
| null | "Confidence could not be computed." |

---

## 4. Failure Mode Handling

### 4.1. Missing Artifact
If a required artifact is missing:
```
"[Section] could not be generated. Artifact missing: {artifact_path}."
```

### 4.2. Parse Error
If an artifact cannot be parsed:
```
"[Section] could not be generated. Data format error in {artifact_path}."
```

### 4.3. Regime Unknown
If regime is UNKNOWN:
```
"Narrative generation is limited. Regime could not be determined.
Only stasis information is available."
```

### 4.4. Stale Data
If data is stale (beyond threshold):
```
"Warning: Data may be stale. Last computed: {timestamp}.
Narrative may not reflect current conditions."
```

---

## 5. Validation Pipeline

### 5.1. Pre-Emission Validation
Before emitting the narrative:

| Check | Action on Failure |
| :--- | :--- |
| Grammar validation | Reject sentence |
| Source binding verification | Reject sentence |
| Regime compatibility | Reject sentence |
| Prohibited word scan | Reject sentence |
| Confidence check | Append uncertainty warning |

### 5.2. Post-Emission Audit
After emitting the narrative:

1.  Log the full narrative with source map.
2.  Store as `narrative_{market}_{date}.json`.
3.  Enable diff comparison with previous narrative.

---

## 6. Anti-Hallucination Checklist

| Control | Description | Status |
| :--- | :--- | :--- |
| ☐ | Every sentence has a source field | Required |
| ☐ | No synonyms or paraphrases | Required |
| ☐ | Missing data is explicitly stated | Required |
| ☐ | Low confidence is amplified | Required |
| ☐ | Stale data is warned | Required |
| ☐ | No forecasts or predictions | Required |
| ☐ | No action language | Required |
| ☐ | Regime gating applied | Required |
| ☐ | Output is logged with lineage | Required |

---

## 7. Hallucination Examples (FORBIDDEN)

| Type | Example | Why Forbidden |
| :--- | :--- | :--- |
| Interpolation | "VIX is rising rapidly." | No rate calculated in artifacts. |
| Forecast | "Volatility will likely remain high." | Predicts future. |
| Recommendation | "Consider reducing exposure." | Implies action. |
| Unsourced claim | "Market sentiment is negative." | Sentiment not in artifacts. |
| Confident unknown | "Regime is probably NEUTRAL." | Confidence not in source. |

---

## 8. Recovery from Compiler Failure

If the compiler cannot produce a valid narrative:

1.  Emit a **fallback narrative**:
    ```
    "Narrative generation failed.
    Reason: {failure_reason}
    Artifacts available: {artifact_list}
    Manual inspection recommended."
    ```

2.  Log the failure with full diagnostics.

3.  Do NOT emit a partial or guessed narrative.
