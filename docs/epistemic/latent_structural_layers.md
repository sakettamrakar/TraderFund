# Latent Structural Layers

**Status:** Epistemic Declaration  
**Scope:** Architecture  
**Authority:** Constitutional — Binding for all future execution harnesses

---

## Purpose

This document formally declares structural layers that are **epistemically unavoidable** for a complete investment intelligence system. These layers exist conceptually and must be anticipated by downstream consumers, even if implementation is deferred.

> [!IMPORTANT]
> A layer marked as LATENT is not optional. It is a placeholder for inevitable complexity. Downstream systems MUST NOT assume these layers will never exist.

---

## Layer Declarations

### 1. Macro / Liquidity Layer

**Position:** L5.5 — Between Feature Layer (L4) and Regime Layer (L6)

**Responsibility:**
- Central bank policy stance (hawkish/dovish)
- Interest rate environment (rising/falling/stable)
- Credit conditions (tight/loose)
- Systemic liquidity (abundant/scarce)
- Cross-asset risk appetite (risk-on/risk-off)

**Primary Question:** "What are the macro constraints governing market behavior?"

**Upstream Dependencies:**
- Feature Layer: Yield curves, credit spreads, monetary aggregates
- External: Fed statements, ECB announcements, central bank balance sheets

**Downstream Consumers:**
- Regime Layer: Macro state constrains regime interpretation
- Factor Layer: Macro determines which factors are favored/penalized

**Why This Layer is Unavoidable:**
Markets do not exist in a vacuum. A "TRENDING_BULL" regime during QE expansion has different characteristics than the same regime during quantitative tightening. Without macro context, regime classification is incomplete.

**Latent Status:**
| Aspect | Status |
|:-------|:-------|
| Epistemic Existence | ✅ EXISTS |
| Implementation | ⏸️ DEFERRED |
| Data Sources | ❌ NOT WIRED |
| Downstream Anticipation | ✅ REQUIRED |

**Failure Mode if Ignored:**
Regime classifier makes decisions without understanding *why* the market behaves as it does. Strategies optimized for one macro regime fail catastrophically when macro shifts.

---

### 2. Flow / Microstructure Layer

**Position:** L5.7 — Parallel to Event Layer (L5)

**Responsibility:**
- Forced market actions (not opinions)
- Mechanical flows from index rebalancing
- Margin call liquidations
- Fund redemption-driven selling
- Options expiration delta hedging
- ETF creation/redemption arbitrage

**Primary Question:** "What forced flows are affecting price action?"

**What Flow IS:**
- Index additions forcing passive fund buying
- Margin calls forcing levered participants to sell
- Month-end rebalancing forcing pension rotation
- Options gamma forcing dealer hedging

**What Flow is NOT:**
- Sentiment (opinions about direction)
- News (information about events)
- Prediction (future price movement)
- Opinion (analyst recommendations)

**How Flow Affects Markets:**
- Flow determines **how fast** and **how far**, not **why**
- Flow can temporarily override slow beliefs
- Flow is transient; structure is persistent
- Flow can amplify or compress regime conditions

**Upstream Dependencies:**
- Feature Layer: Volume, order flow imbalance, options open interest
- External: Index reconstitution announcements, fund flow data

**Downstream Consumers:**
- Signal Layer: Flow context modulates signal timing
- Execution Layer: Flow affects optimal execution timing

**Latent Status:**
| Aspect | Status |
|:-------|:-------|
| Epistemic Existence | ✅ EXISTS |
| Implementation | ⏸️ DEFERRED |
| Data Sources | ❌ NOT WIRED |
| Downstream Anticipation | ✅ REQUIRED |

**Failure Mode if Ignored:**
System cannot explain sudden violent moves. A 5% move in 10 minutes looks identical to a 5% move over 5 days. Flow context is essential for timing and risk management.

---

### 3. Volatility Geometry Layer

**Position:** L5.8 — Parallel to Flow Layer

**Responsibility:**
- Volatility term structure (contango/backwardation)
- Skew (put/call implied volatility differential)
- Convexity (how volatility responds to spot moves)
- Tail risk pricing (far OTM options pricing)
- Implied vs realized volatility spread

**Primary Question:** "How is the market pricing uncertainty?"

**What This Layer Captures:**
- Market expectations embedded in options prices
- Risk premium demanded for tail events
- Hedging demand vs speculation balance
- Forward-looking fear/greed beyond spot price

**Upstream Dependencies:**
- Feature Layer: Options prices, implied volatility surfaces
- External: VIX, VVIX, skew indices

**Downstream Consumers:**
- Regime Layer: Volatility geometry informs regime stability
- Strategy Layer: Position sizing adjustments based on tail risk

**Latent Status:**
| Aspect | Status |
|:-------|:-------|
| Epistemic Existence | ✅ EXISTS |
| Implementation | ⏸️ DEFERRED |
| Data Sources | ❌ NOT WIRED (requires options data) |
| Downstream Anticipation | ✅ REQUIRED |

**Failure Mode if Ignored:**
System uses only realized volatility, missing forward-looking signals from options markets. Tail risk events appear as "surprises" when they were priced into options.

---

## Integration with Structure Stack Vision

These latent layers integrate into the existing 14-layer Structure Stack as follows:

```
Zone A: Structural Backbone (Truth)
  L1: Reality Layer (Ingestion)
  L2: Time Layer (Alignment)
  L3: Object Layer (Identity)
  L4: Feature Layer (Measurement)

Zone B: Interpretive Intelligence (Understanding)
  L5:   Event Layer (Detection)
  L5.5: Macro / Liquidity Layer [LATENT]      ← NEW
  L5.7: Flow / Microstructure Layer [LATENT]  ← NEW
  L5.8: Volatility Geometry Layer [LATENT]    ← NEW
  L6:   Regime Layer (Environment)
  L7:   Narrative Layer (Context)
  L8:   Signal Layer (Observation)
  L9:   Belief Layer (Synthesis)

Zone C: Expression & Execution (Action)
  L10-L14: [Unchanged]
```

---

## Invariants for Downstream Systems

1. **No assumption of absence**: Code must not assume these layers will never exist
2. **Graceful degradation**: When latent layers are not implemented, downstream layers must proceed with reduced confidence
3. **Interface anticipation**: Placeholder interfaces should exist even if implementations are stubs
4. **Documentation readiness**: When implementation begins, only the engine changes — not the epistemic definition

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| v1.0 | 2026-01-24 | Initial declaration of latent layers |
