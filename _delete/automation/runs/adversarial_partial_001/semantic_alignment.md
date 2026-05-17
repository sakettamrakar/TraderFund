# Semantic Alignment Tree — adversarial_partial_001

**Generated**: 2026-02-16T23:58:58.240996
**Recommendation**: REJECT
**Final Score**: 0.0150

---

## Scoring Breakdown

- Base score = mean(0.10, 0.33) = 0.22
- Missing requirements penalty: -0.10 × 2 = -0.20
-   ▸ Missing: Add error rate tracking with a counter
-   ▸ Missing: Add a health check endpoint that returns strategy status
- Total penalty = 0.20
- Final score = max(0, 0.22 - 0.20) = 0.0150
- Recommendation = REJECT

---

## Alignment (Pass 1: Alignment Judge)

| Metric | Score |
|--------|-------|
| Intent Match | 0.10 |
| Plan Match | 0.33 |
| Scope Respected | ✅ |

---

## Drift (Pass 2: Drift Prosecutor)

- **Overreach Detected**: ✅ No

### Missing Requirements (2)
- ❌ Add error rate tracking with a counter
- ❌ Add a health check endpoint that returns strategy status

---

## Contract Violations

None.

---

## Explanation Tree

- Intent: Implement full observability for the momentum strategy pipeline.
- Plan Objective: Add observability to momentum pipeline
- Alignment Judge: intent_match=0.10, plan_match=0.33
- ❌ Missing: Add error rate tracking with a counter
- ❌ Missing: Add a health check endpoint that returns strategy status
- ⚠ Coverage gap: Plan targets 'src/api/health.py' but it was not modified.

---

## Coverage Flags

- ⚠ Coverage gap: Plan targets 'src/api/health.py' but it was not modified.