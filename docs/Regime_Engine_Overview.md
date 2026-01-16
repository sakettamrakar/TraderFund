# Regime Engine Overview

> **CHANGELOG**  
> - 2026-01-16: Created as authoritative overview from live implementation  
> - Synced with `traderfund/regime/` codebase

---

## What is a Regime?

A **Market Regime** is a persistent, observable state of market behavior that determines which trading strategies are likely to succeed.

Think of it as **weather for trading**:
- You check the weather before going outside
- You check the regime before deploying capital

---

## Core Principle

> **Strategies ask:** "Is there a trade?"  
> **Regime Layer answers:** "Is it safe to play?"

---

## Four Dimensions of Regime Detection

### 1. Trend (Directional Persistence)
- How strongly is price moving in one direction?
- High trend = momentum strategies work
- Low trend = mean reversion works

### 2. Volatility (Amplitude of Variance)
- How much is price moving relative to baseline?
- High vol = wider stops, smaller size
- Low vol = tighter stops, larger size ok

### 3. Liquidity (Execution Efficiency)
- Can we enter/exit without excessive slippage?
- Low liquidity = avoid or reduce size

### 4. Event Pressure (External Catalysts)
- Are news/earnings/announcements driving price?
- High pressure = technicals may fail

---

## Why Regime Comes BEFORE Strategies

```
Market Data → Regime Detection → Strategy Gate → Execution
```

1. **Data arrives**
2. **Regime Engine classifies the environment**
3. **Incompatible strategies are blocked/throttled**
4. **Only compatible strategies execute**

This order is **non-negotiable**. Strategies cannot override regime.

---

## Explicit Non-Goals

The Regime Engine does **NOT**:

| ❌ Does NOT | Reason |
|-------------|--------|
| Generate trade signals | That's the strategy's job |
| Predict future prices | Regime is descriptive, not predictive |
| Optimize for PnL | Regime optimizes for environment detection |
| Replace human judgment | Regime is a filter, not a decision-maker |

---

## System Architecture

```
[Market Data]
     ↓
[Indicator Layer] → Trend, Vol, Liquidity, Events
     ↓
[Regime Engine] → Classifies into 7 states
     ↓
[Strategy Gate] → Blocks/Throttles incompatible strategies
     ↓
[Dashboard] → Human visibility
```

---

## What NOT To Do

> **CRITICAL: Read this before making changes**

- ❌ Do NOT add new indicators without spec revision
- ❌ Do NOT override regime manually during trading
- ❌ Do NOT trade against regime out of frustration
- ❌ Do NOT treat regime as a trade signal
- ❌ Do NOT change thresholds during market hours

---

## Document Status

| Section | Status |
|---------|--------|
| Core principle | FROZEN |
| Four dimensions | FROZEN |
| Non-goals | FROZEN |
| Architecture | FROZEN |
