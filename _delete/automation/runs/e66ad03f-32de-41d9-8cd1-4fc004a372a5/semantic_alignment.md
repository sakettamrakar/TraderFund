# Semantic Alignment Tree â€” e66ad03f-32de-41d9-8cd1-4fc004a372a5

**Generated**: 2026-02-18T17:07:35.710867
**Recommendation**: REVIEW
**Final Score**: 0.9500

---

## Scoring Breakdown

- Base score = mean(1.00, 1.00) = 1.00
- Semantic mismatch penalty: -0.05 × 1 = -0.05
- Total penalty = 0.05
- Final score = max(0, 1.00 - 0.05) = 0.9500
- Recommendation = REVIEW

---

## Alignment (Pass 1: Alignment Judge)

| Metric | Score |
|--------|-------|
| Intent Match | 1.00 |
| Plan Match | 1.00 |
| Scope Respected | âœ… |

---

## Drift (Pass 2: Drift Prosecutor)

- **Overreach Detected**: âœ… No

### Semantic Mismatch (1)
- ðŸ”´ The regime classification logic in `_get_regime_category` is brittle. It compares the input `behavior` directly against `MarketBehavior` enum members (`if behavior in [MarketBehavior.MEAN_REVERTING_LOW_VOL, ...]`). If the `regime_state` dictionary contains the behavior as a string (e.g., from JSON deserialization), this comparison will fail. Consequently, all regimes would be misclassified as 'TRANSITION', making the 'TRENDING' validation logic unreachable and the 'CHOP' validation indistinguishable from 'TRANSITION'.

---

## Contract Violations

None.

---

## Explanation Tree

- Intent: 7. l3 — meta-analysis success
7. l3 — meta-analysis success
- Primary Goal: 7. l3 — meta-analysis success
- Expected Beh
- Plan Objective: 7. l3 — meta-analysis success
- Alignment Judge: intent_match=1.00, plan_match=1.00
- 🔴 Mismatch: The regime classification logic in `_get_regime_category` is brittle. It compares the input `behavior` directly against `MarketBehavior` enum members (`if behavior in [MarketBehavior.MEAN_REVERTING_LOW_VOL, ...]`). If the `regime_state` dictionary contains the behavior as a string (e.g., from JSON deserialization), this comparison will fail. Consequently, all regimes would be misclassified as 'TRANSITION', making the 'TRENDING' validation logic unreachable and the 'CHOP' validation indistinguishable from 'TRANSITION'.