# Genesis Production Rules

**Status:** FROZEN (v1.0)
**Last Updated:** 2026-01-17

## 1. Production Thresholds

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| `MIN_SEVERITY_FOR_GENESIS` | **60.0** | HIGH events (90) and MEDIUM events (70) pass. LOW events (40) are filtered as noise. |
| `MAX_NARRATIVES_PER_DAY` | **5** | Prevents narrative explosion. Ensures human reviewability. |

## 2. Admission Rules

| Severity | Admission | Notes |
| :--- | :--- | :--- |
| **HIGH (90)** | Always Allowed | Disruptive events must be captured immediately. |
| **MEDIUM (70)** | Subject to Daily Cap | Standard news, limited by `MAX_NARRATIVES_PER_DAY`. |
| **LOW (40)** | Rejected (unless accumulated) | Noise by default. May promote via Accumulation Logic. |

## 3. Why Genesis is Conservative

1.  **Signal-to-Noise Ratio:** Financial news is noisy. Most stories are irrelevant to trading decisions.
2.  **Attention Scarcity:** Human operators have limited attention. Too many narratives dilutes focus.
3.  **Regime Dampening:** Even admitted narratives are further dampened by Regime Enforcement. Being conservative upstream compounds safety.
4.  **Explainability:** Fewer narratives are easier to audit and understand.

## 4. Cap Enforcement

- The `MAX_NARRATIVES_PER_DAY` cap is enforced **per market, per calendar day (UTC)**.
- HIGH severity events **bypass** the cap. They are too important to drop.
- MEDIUM events are rejected once cap is reached.
- Accumulated (promoted) events are treated as MEDIUM and respect the cap.
