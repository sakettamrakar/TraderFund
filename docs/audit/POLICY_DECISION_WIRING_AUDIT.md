# Policy & Decision Wiring Audit — Consolidated

> Consolidated from 5 policy/decision audit files. Originals moved to `_delete/audit/`.
> Date: Jan 30, 2026

---

## 1. Regime Gate Verification

**Component**: `RegimeContextBuilder` v2.0.0-IGNITION

### US Market
- Logic: `Price > SMA50 AND VIX < 25` → BULLISH; `Price < SMA200` → BEARISH
- Output: **BEARISH** (correctly identified downtrend in data)
- Fail-closed: empty/gap data → `UNKNOWN` (refuses to guess)

### India Market
- Logic: `Price > SMA50` (surrogate)
- Output: verification output truncated — needs investigation
- Recommendation: verify India didn't crash; confirm Price/SMA values

---

## 2. Decision Policy Engine

### US Market
- Input: BEARISH regime + NEUTRAL liquidity + TECH_LEAD breadth
- Output: `ACTIVE`
- Permissions: `ALLOW_SHORT_ENTRY` (bearish), `ALLOW_POSITION_HOLD` (standard), `ALLOW_LONG_ENTRY_SPECIAL` (tech divergence)
- Verdict: correctly identified "Bear Market Rationally" state

### India Market
- Input: UNKNOWN (degraded)
- Output: `RESTRICTED` | Permissions: `OBSERVE_ONLY`
- Reason: `DEGRADED_PROXY_STATE` — Golden Rule applied

**Artifacts**: `decision_policy_{market}.json` — authoritative source of permission for dashboard

---

## 3. Fragility Engine

### Design (Frozen Jan 30)
- **Subtractive Principle**: verified — only blocks intents, never adds permissions
- **Market Isolation**: verified — `FragilityEngine.evaluate(market)` per-market
- **India Hard-Stop**: forced `NOT_EVALUATED` with `SYSTEMIC_STRESS` block list
- **Invariants**: `INV-NO-CAPITAL`, `INV-NO-EXECUTION`, `INV-PROXY-CANONICAL` confirmed

### Wiring Verification
**US Market** (critical test):
- Input: Decision Policy allows `ALLOW_LONG_ENTRY_SPECIAL`, `ALLOW_SHORT_ENTRY`; VIX = 101.58
- Fragility detected Volatility > 35 → `SYSTEMIC_STRESS`
- Constraints: `BLOCK_LONG`, `BLOCK_SHORT`
- Result: only `ALLOW_POSITION_HOLD` remains
- **Verdict**: circuit breaker successfully tripped, subtractive logic proven

**India Market**:
- Skipped evaluation → `NOT_EVALUATED`, forced `OBSERVE_ONLY`
- Epistemic honesty maintained

### Pipeline: `Decision → Fragility → Final Output`
`final_authorized_intents` in `fragility_context_US.json` is the sole authority for execution.

---

## 4. Dashboard Integration

### Policy State Card (`PolicyStateCard.jsx`)
- Integrated into `IntelligencePanel.jsx`
- Fetches from `/api/intelligence/policy/{market}`
- Shows: ACTIVE vs RESTRICTED, permissions, reason, epistemic health
- Degraded state: red overlay (e.g., India)

### Epistemic Health Check (`EpistemicHealthCheck.jsx`)
- Integrated into `SystemStatus.jsx` (top banner)
- Shows: Truth Epoch, Proxy Status

### Visual Compliance
- Read-only: no interactive policy-changing elements
- Market isolation: components respect `market={market}` prop
- Honesty: stale/missing data → "OFFLINE" or "Loading", never fake values

---

## 5. Full Pipeline Integrity

```
Regime Gate (What market state?)
    → Decision Policy Engine (What is allowed?)
        → Fragility Engine (Stress veto?)
            → Final Authorized Intents (Dashboard display)
```

| Layer | US Result | India Result |
| :--- | :--- | :--- |
| Regime | BEARISH | UNKNOWN (degraded) |
| Decision | ACTIVE (short+hold+special long) | RESTRICTED (observe only) |
| Fragility | SYSTEMIC_STRESS (blocks entries) | NOT_EVALUATED |
| Final | ALLOW_POSITION_HOLD only | OBSERVE_ONLY |
