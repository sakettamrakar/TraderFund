# Flow / Microstructure Layer

**Status:** Epistemic Declaration  
**Scope:** Architecture — Forced Flow Documentation  
**Authority:** Constitutional — This layer exists even if unimplemented

---

## Purpose

This document formally declares the **Flow / Microstructure Layer** as an epistemically inevitable component of the investment intelligence system. Flow represents forced market actions — mechanical, non-discretionary buying or selling that affects price discovery.

> [!IMPORTANT]
> Flow is NOT sentiment. Flow is NOT opinion. Flow explains the **speed** and **violence** of moves, not their direction or cause.

---

## Definition

**What is Flow?**

Flow represents the aggregate of forced, mechanical, or non-discretionary trading activity in a market. It is distinct from:
- **Fundamentals**: Why an asset should be valued at X
- **Technicals**: Statistical patterns in price action
- **Sentiment**: Market participants' opinions on direction

Flow is the **physics** of market microstructure — the mechanics of how orders interact with liquidity.

---

## Types of Forced Flow

### 1. Index Rebalancing Flow

| Characteristic | Description |
|:---------------|:------------|
| **Trigger** | Index reconstitution announcements |
| **Direction** | Mechanical: Buy additions, Sell deletions |
| **Size** | Proportional to passive AUM tracking the index |
| **Timing** | Concentrated around effective date (T-1 to T+1) |

**Example:** When a stock is added to S&P 500, passive funds must buy it regardless of price, creating predictable demand.

### 2. Margin Call Liquidation Flow

| Characteristic | Description |
|:---------------|:------------|
| **Trigger** | Portfolio drawdown breaching margin limits |
| **Direction** | Forced selling |
| **Size** | Position-dependent |
| **Timing** | Immediate, often intraday |

**Example:** Levered long fund experiences drawdown → margin call → forced liquidation → amplified selling pressure.

### 3. Fund Redemption Flow

| Characteristic | Description |
|:---------------|:------------|
| **Trigger** | Investor withdrawal requests |
| **Direction** | Forced selling to meet redemptions |
| **Size** | Proportional to redemption amount |
| **Timing** | End-of-day, month-end concentrations |

**Example:** Mutual fund faces redemptions → must sell holdings → selling pressure regardless of fundamentals.

### 4. Options Expiration / Delta Hedging Flow

| Characteristic | Description |
|:---------------|:------------|
| **Trigger** | Options approaching expiration, gamma exposure |
| **Direction** | Dealer hedging creates positive feedback loops |
| **Size** | Gamma-weighted |
| **Timing** | Concentrated around expiration, especially last hour |

**Example:** Large open interest at a strike → dealers delta hedge → price pins to strike or accelerates through it.

### 5. ETF Arbitrage Flow

| Characteristic | Description |
|:---------------|:------------|
| **Trigger** | Premium/discount between ETF and NAV |
| **Direction** | Arbitrage creation/redemption |
| **Size** | Proportional to deviation |
| **Timing** | Intraday, especially market open/close |

---

## Epistemic Framing

### What Flow IS

- A representation of forced, non-discretionary market actions
- An explanation for the speed, compression, and violence of moves
- A factor that can temporarily override slow beliefs
- Transient — flows complete and then stop

### What Flow is NOT

- Sentiment (opinions about direction)
- News (information about events)
- Prediction (forward-looking)
- Causation (flow is effect, not cause)

### How Flow Interacts with Other Layers

```
Flow affects: HOW FAST and HOW FAR
Flow does NOT affect: WHY

Example:
  Fundamental: "Company X is undervalued"     → WHY to buy
  Technical:   "Breakout above resistance"    → WHEN to buy
  Flow:        "Index addition on Friday"     → HOW FAST it will move
```

---

## Temporal Dynamics

| Property | Slow Beliefs (Regime, Narrative) | Fast Flow (Microstructure) |
|:---------|:---------------------------------|:---------------------------|
| Persistence | Days to weeks | Minutes to hours |
| Predictability | Statistical | Mechanical |
| Override potential | Low | High (temporarily) |
| Mean reversion | Slow | Fast |

**Key Principle:** Flow can temporarily override slow beliefs but cannot permanently alter market structure. A forced liquidation may push price below fair value, but fundamentals eventually reassert.

---

## Flow Layer Output (Future Schema)

When implemented, the Flow Layer will produce:

```python
class FlowState:
    timestamp: datetime
    
    # Flow indicators
    rebalance_pressure: float     # -1.0 (selling) to +1.0 (buying)
    gamma_exposure: float         # Dealer hedging pressure
    liquidity_score: float        # Order book depth
    
    # Event flags
    index_rebalance_imminent: bool
    options_expiry_today: bool
    month_end: bool
    
    # Impact estimate
    expected_compression: float   # How much faster than normal
    expected_amplitude: float     # How much larger than normal
```

---

## Latent Status

| Aspect | Status |
|:-------|:-------|
| Epistemic Existence | ✅ EXISTS |
| Definition | ✅ DOCUMENTED (this document) |
| Implementation | ⏸️ DEFERRED |
| Data Sources | ❌ NOT WIRED |
| Downstream Anticipation | ✅ REQUIRED |

---

## Invariants for Downstream Systems

1. **Flow does not cause, it amplifies**: Flow layer outputs must be treated as modifiers, not signals
2. **Flow is mechanical, not discretionary**: Do not conflate flow with sentiment
3. **Flow is transient**: Do not build long-term strategies on flow alone
4. **Absence of flow data ≠ absence of flow**: When unimplemented, assume baseline flow state

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| v1.0 | 2026-01-24 | Initial Flow/Microstructure layer declaration |
