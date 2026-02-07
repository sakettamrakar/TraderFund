# Integration Reality Run — Narrative Failure Matrix

## 1. Purpose
This matrix validates narrative outputs against the grammar, regime gating, and hallucination controls.

---

## 2. Validation Categories

| Category | Description |
| :--- | :--- |
| **GRAMMAR** | Vocabulary and sentence structure compliance |
| **REGIME** | Regime-appropriate content |
| **SOURCE** | Every claim traceable to artifact |
| **HALLUCINATION** | No invented or inferred content |

---

## 3. US Market Narrative Validation

### 3.1. Sample Narrative Sentences

| Sentence | GRAMMAR | REGIME | SOURCE | HALLUCINATION | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| "The current regime is BEARISH." | ✅ | ✅ | ✅ | ✅ | PASS |
| "Volatility level: 101.58, classified as extreme." | ✅ | ✅ | ✅ | ✅ | PASS |
| "Long entry is blocked due to regime." | ✅ | ✅ | ✅ | ✅ | PASS |
| "You should consider exiting positions." | ❌ | — | — | — | **FAIL: Prohibited verb "should"** |
| "Market will likely continue falling." | ❌ | — | — | ❌ | **FAIL: Forecast language** |

### 3.2. Failure Summary (US)

| Category | Violations | Examples |
| :--- | :--- | :--- |
| GRAMMAR | 0 | — |
| REGIME | 0 | — |
| SOURCE | 0 | — |
| HALLUCINATION | 0 | — |

**Verdict**: US narrative PASSES all checks (no violations in actual output).

---

## 4. India Market Narrative Validation

### 4.1. Sample Narrative Sentences

| Sentence | GRAMMAR | REGIME | SOURCE | HALLUCINATION | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| "The current regime is NEUTRAL." | ✅ | ✅ | ✅ | ✅ | PASS |
| "Volatility level: 13.37, classified as normal." | ✅ | ✅ | ✅ | ✅ | PASS |
| "Hold and rebalance are permitted." | ✅ | ✅ | ✅ | ✅ | PASS |
| "No directional entries under NEUTRAL regime." | ✅ | ✅ | ✅ | ✅ | PASS |
| "This is a good time to accumulate." | ❌ | ❌ | ❌ | ❌ | **FAIL: Recommendation** |

### 4.2. Failure Summary (India)

| Category | Violations | Examples |
| :--- | :--- | :--- |
| GRAMMAR | 0 | — |
| REGIME | 0 | — |
| SOURCE | 0 | — |
| HALLUCINATION | 0 | — |

**Verdict**: India narrative PASSES all checks (no violations in actual output).

---

## 5. Cross-Narrative Checks

| Check | Result |
| :--- | :--- |
| US narrative mentions India | ✅ PASS (no cross-market) |
| India narrative mentions US | ✅ PASS (no cross-market) |
| Both include provenance timestamps | ✅ PASS |
| Both include regime disclosure | ✅ PASS |

---

## 6. Prohibited Patterns Scan

| Pattern | US Occurrences | India Occurrences |
| :--- | :--- | :--- |
| "should" | 0 | 0 |
| "recommend" | 0 | 0 |
| "opportunity" | 0 | 0 |
| "target" | 0 | 0 |
| "buy" (as action) | 0 | 0 |
| "sell" (as action) | 0 | 0 |
| "profit" | 0 | 0 |
| "will" (forecast) | 0 | 0 |

**All prohibited patterns: 0 occurrences.**

---

## 7. Conclusion

| Market | Narrative Status |
| :--- | :--- |
| US | ✅ COMPLIANT |
| INDIA | ✅ COMPLIANT |

No narrative failures detected. Grammar and hallucination controls are functioning correctly.
