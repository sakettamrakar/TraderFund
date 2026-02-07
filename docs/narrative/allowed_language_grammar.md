# Narrative Allowed Language Grammar

## 1. Purpose
This document defines the **allowed vocabulary and sentence structures** for the Narrative Compiler.
Any output not conforming to this grammar is a violation and must be rejected.

---

## 2. Allowed Verbs

### 2.1. Descriptive Verbs (ALLOWED)
| Verb | Usage |
| :--- | :--- |
| is / are | "The regime **is** BEARISH." |
| was | "The last tick **was** 20 minutes ago." |
| shows | "Volatility **shows** elevated levels." |
| indicates | "Breadth **indicates** tech leadership." |
| permits / blocks | "Policy **permits** holding." |
| applies | "Fragility **applies** constraints." |
| detects | "The system **detects** stress." |
| computes / computed | "Regime **computed** at 05:00." |

### 2.2. Prohibited Verbs (NEVER USE)
| Verb | Reason |
| :--- | :--- |
| should | Implies recommendation |
| must | Implies obligation |
| will | Implies forecast |
| recommends | Implies advice |
| expects | Implies prediction |
| suggests | Implies recommendation |
| buy / sell | Implies action |
| profit / gain | Implies capital outcome |

---

## 3. Allowed Nouns

### 3.1. State Nouns (ALLOWED)
| Noun | Context |
| :--- | :--- |
| regime | "The **regime** is NEUTRAL." |
| factor | "Volatility **factor** is elevated." |
| permission | "Long entry **permission** is granted." |
| constraint | "Stress **constraint** applied." |
| state | "Policy **state** is ACTIVE." |
| condition | "Market **conditions** are mixed." |

### 3.2. Value Nouns (ALLOWED)
| Noun | Context |
| :--- | :--- |
| level | "VIX **level** is 25.4." |
| threshold | "Above critical **threshold**." |
| timestamp | "Computed **timestamp**." |
| confidence | "With 0.8 **confidence**." |

### 3.3. Prohibited Nouns (NEVER USE)
| Noun | Reason |
| :--- | :--- |
| opportunity | Implies value judgment |
| target | Implies price forecast |
| profit / loss | Implies capital |
| position | Implies holdings |
| portfolio | Implies capital |
| recommendation | Implies advice |

---

## 4. Sentence Templates

### 4.1. Regime Sentences
```
"The current regime is {regime_code}."
"Regime state: {regime_label}."
"Market is operating under {regime_code} conditions."
"Regime computed at {timestamp}."
```

### 4.2. Factor Sentences
```
"{factor_name} factor is {factor_state}."
"{factor_name}: {value} ({state})."
"Volatility level: {vol_value}, classified as {vol_state}."
"Liquidity conditions are {liq_state} (yield: {yield_value}%)."
```

### 4.3. Policy Sentences
```
"Policy state is {policy_state}."
"The following permissions are granted: {permissions_list}."
"The following actions are blocked: {blocked_list}."
"Policy reason: {reason}."
```

### 4.4. Fragility Sentences
```
"Stress state is {stress_state}."
"Fragility layer applies: {constraints_list}."
"Final authorized intents: {intents_list}."
"Stress reason: {stress_reason}."
```

### 4.5. Uncertainty Sentences
```
"Confidence level: {confidence}."
"Factor {factor_name} could not be computed (data missing)."
"Regime is UNKNOWN — insufficient data."
"Parity status: DEGRADED ({gap_count} gaps remaining)."
```

---

## 5. Phrase Constructs

### 5.1. Causal Phrases (ALLOWED)
| Pattern | Example |
| :--- | :--- |
| "due to..." | "Blocked **due to** SYSTEMIC_STRESS." |
| "because of..." | "Restricted **because of** volatility spike." |
| "as a result of..." | "Permissions reduced **as a result of** regime flip." |

### 5.2. Conditional Phrases (ALLOWED)
| Pattern | Example |
| :--- | :--- |
| "if...then" | "**If** stress abates, **then** permissions may change." |
| "when...is" | "**When** parity **is** achieved, evaluation resumes." |

### 5.3. Prohibited Phrases
| Pattern | Reason |
| :--- | :--- |
| "you should..." | Recommendation |
| "consider..." | Recommendation |
| "likely to..." | Forecast |
| "expected to..." | Forecast |
| "buy now..." | Action |
| "sell before..." | Action |

---

## 6. Punctuation and Formatting

*   Use periods for statements.
*   Use colons for labels (e.g., "Regime: BEARISH").
*   Use bullet points for lists.
*   No exclamation marks (avoids urgency implication).
*   No question marks (narrative is declarative, not interrogative).
