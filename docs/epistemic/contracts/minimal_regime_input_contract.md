# Minimal Regime Input Contract

**Status**: Constitutional — Binding  
**Scope**: Evolution Phase (EV) — Regime Computation  
**Date**: 2026-01-25  
**Version**: 1.0

---

## 1. Purpose

This contract defines the **minimal required inputs** for regime state computation. It is the single source of truth for regime data requirements.

**Guiding Principle**: A regime that runs on incomplete data is worse than no regime at all.

---

## 2. Required Symbols (Exhaustive & Minimal)

The following symbols are **REQUIRED** for baseline regime viability:

| Symbol | Role | Description |
|:-------|:-----|:------------|
| **SPY** | Equity Proxy | S&P 500 ETF |
| **QQQ** | Equity Proxy | NASDAQ 100 ETF |
| **VIX** | Volatility Proxy | CBOE Volatility Index |
| **^TNX** | Rates Proxy | 10-Year Treasury Yield |
| **^TYX** | Rates Proxy | 30-Year Treasury Yield |
| **HYG** | Credit Proxy | High Yield Corporate Bond ETF |
| **LQD** | Credit Proxy | Investment Grade Corporate Bond ETF |

### Contract Statement

> **No other symbols are required for baseline regime viability.**
>
> These 7 symbols constitute the exhaustive minimal set.
> Additional symbols may enhance regime quality but are not mandatory.

---

## 3. Required Historical Depth

### Minimum Lookback Window

| Requirement | Value |
|:------------|:------|
| **Minimum History** | ≥ 3 years (756 trading days) |
| **Recommended History** | ≥ 5 years (1260 trading days) |

### Contract Statement

> **No regime computation is permitted before the minimum lookback window is satisfied.**
>
> If any required symbol has fewer than 756 trading days of history,
> the regime state MUST be `UNDEFINED`.

---

## 4. Frequency & Granularity

### Requirements

| Aspect | Value |
|:-------|:------|
| **Frequency** | Daily bars only |
| **Granularity** | Close prices |
| **Mixed Frequency** | NOT ALLOWED |

### Contract Statement

> **Only daily bar data is permitted for regime computation.**
>
> No mixed-frequency inference is allowed.
> Intraday data must not be used for regime state computation.

---

## 5. Temporal Alignment Rules

### Requirements

| Rule | Enforcement |
|:-----|:------------|
| **Intersection Only** | Regime state computed only on intersection of timestamps |
| **Forward-Fill** | NOT ALLOWED |
| **Interpolation** | NOT ALLOWED |
| **Silent Gap Bridging** | NOT ALLOWED |

### Contract Statement

> **Regime state is computed ONLY on dates where ALL required symbols have data.**
>
> Forward-filling across symbols is FORBIDDEN.
> Silent interpolation is FORBIDDEN.
> If timestamps do not align, those dates are EXCLUDED from regime computation.

---

## 6. Failure Semantics (CRITICAL)

### Explicit Failure Conditions

| Condition | Result |
|:----------|:-------|
| **Missing Symbol** | regime = `NOT_VIABLE` |
| **Insufficient History** | regime = `NOT_VIABLE` |
| **Temporal Misalignment** | regime = `NOT_VIABLE` |
| **Partial Inputs** | regime = `NOT_VIABLE` |

### Contract Statement

> **`UNDEFINED` regime is a CORRECT and EXPECTED outcome under contract violation.**
>
> When this contract is not satisfied, the regime state MUST be:
> - `NOT_VIABLE` (if known to be unsatisfiable)
> - `UNDEFINED` (if indeterminate)
>
> **Running regime logic on incomplete data is FORBIDDEN.**

---

## 7. Contract Binding

This contract binds the following system components:

| Component | Binding |
|:----------|:--------|
| **Regime Computation** | Must validate contract before computing |
| **EV-RG-RUN Audits** | Must check contract compliance |
| **Decision Plane** | Must not use regime state if contract violated |
| **Strategy Evaluation** | Must treat `UNDEFINED` regime as first-class signal |

---

## 8. Evidence Requirements

Contract satisfaction MUST be evidenced by:

| Evidence | Source |
|:---------|:-------|
| Symbol Availability | `EV-RG-RUN-1` output |
| Historical Depth | `EV-RG-RUN-3` output |
| Temporal Alignment | `EV-RG-RUN-4` output |
| State Viability | `EV-RG-RUN-5` output |

---

## 9. Amendment Process

This contract may only be amended through:

1. Formal decision (D-series)
2. Ledger entry
3. DID artifact

**No silent relaxation of requirements is permitted.**

---

## 10. Cross-Reference

| Document | Relationship |
|:---------|:-------------|
| [regime_observability_audit.md](file:///c:/GIT/TraderFund/docs/epistemic/governance/regime_observability_audit.md) | Audit definition |
| [regime_ingestion_obligations.md](file:///c:/GIT/TraderFund/docs/epistemic/governance/regime_ingestion_obligations.md) | Ingestion obligations |
| [task_graph.md](file:///c:/GIT/TraderFund/docs/epistemic/roadmap/task_graph.md) | EV-RG-RUN task definitions |
