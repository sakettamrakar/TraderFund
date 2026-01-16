# Regime Taxonomy

> **CHANGELOG**  
> - 2026-01-16: Created from live implementation (`traderfund/regime/types.py`)  
> - Status: **FROZEN** — Do not modify without architecture review

---

## The 7 Regime States

These are the **only** valid regime states. Adding or removing states requires a full architecture review.

---

### 1. TRENDING_NORMAL_VOL

**What it means:**
- Price is moving directionally with stable variance
- Pullbacks are shallow and predictable
- Trend-following strategies thrive

**Typical trader mistakes:**
- Fading the trend ("it's too high")
- Taking profits too early
- Counter-trend scalping

**What ends this regime:**
- Volatility expansion (news, earnings)
- Trend exhaustion (momentum divergence)

---

### 2. TRENDING_HIGH_VOL

**What it means:**
- Price is moving directionally but with violent swings
- Deep pullbacks within the trend
- Risk of gaps and stop-hunting

**Typical trader mistakes:**
- Using normal-sized stops (get stopped out by noise)
- Over-leveraging
- Holding through announcements

**What ends this regime:**
- Volatility collapse (exhaustion)
- Trend reversal

---

### 3. MEAN_REVERTING_LOW_VOL

**What it means:**
- Price is range-bound with low amplitude
- Support/resistance hold repeatedly
- Boring, choppy, rotational

**Typical trader mistakes:**
- Chasing breakouts (they fail)
- Momentum trading (no momentum exists)
- Expecting trend continuation

**What ends this regime:**
- Volatility expansion
- Genuine breakout with volume

---

### 4. MEAN_REVERTING_HIGH_VOL

**What it means:**
- Price is range-bound but with violent swings
- "Stop hunting" behavior
- False breakouts in both directions

**Typical trader mistakes:**
- Trading with narrow stops
- Trusting range boundaries
- Over-trading

**What ends this regime:**
- Directional resolution (trend emergence)
- Volatility collapse

---

### 5. EVENT_DOMINANT

**What it means:**
- News/events are driving price
- Technicals may not apply
- Discontinuous pricing but still tradable

**Typical trader mistakes:**
- Ignoring the news
- Using technical-only strategies
- Fighting the narrative

**What ends this regime:**
- Event passes
- Market digests information

---

### 6. EVENT_LOCK

**What it means:**
- Binary outcome pending (earnings, FOMC, etc.)
- Market is frozen or extremely thin
- No statistical edge exists

**Typical trader mistakes:**
- Holding positions through the event
- Taking new positions
- Believing you can predict the outcome

**What ends this regime:**
- Event occurs
- Outcome is known

**Rule:** **ALL STRATEGIES BLOCKED** during EVENT_LOCK

---

### 7. UNDEFINED

**What it means:**
- Conflicting signals
- Cannot reliably classify
- Statistical properties are unstable

**Typical trader mistakes:**
- Forcing a trade anyway
- Trusting weak signals
- Ignoring the uncertainty

**What ends this regime:**
- Clarity emerges
- One dimension dominates

**Rule:** Default to **CAUTIOUS** posture

---

## Directional Bias (Overlay)

Each regime also has a directional bias:

| Bias | Meaning |
|------|---------|
| BULLISH | Market structure suggests upside |
| BEARISH | Market structure suggests downside |
| NEUTRAL | No directional edge |

**Example:** `TRENDING_NORMAL_VOL + BULLISH` = Strong uptrend, safe for longs

---

## Document Status

**STATUS: FROZEN**

This taxonomy matches `traderfund/regime/types.py:MarketBehavior`.

Do not add, remove, or rename states without:
1. Architecture review
2. Code update
3. Test coverage
4. Documentation sync
