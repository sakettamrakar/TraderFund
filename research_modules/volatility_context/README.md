# Volatility & Market Context Module (Module B)

## RESEARCH-ONLY

> ⚠️ **WARNING**: This module is strictly for research purposes.
> It MUST NOT be used to filter or size live trades.

---

## Purpose

This module answers a single question:

> "What kind of market environment is this?"

It provides **labels** and **measurements** for market conditions. It does NOT make trade decisions.

---

## What This Module MEASURES

✅ **Volatility Metrics:**
- ATR (Average True Range)
- Daily range (absolute and %)
- Rolling standard deviation
- Range expansion/contraction ratio

✅ **Regime Labels:**
- LOW / NORMAL / HIGH volatility
- TRENDING / RANGING / UNCLEAR market
- EXPANSION / COMPRESSION range state

---

## What This Module Does NOT DECIDE

❌ "This is a good time to trade"
❌ "Skip this signal because volatility is high"
❌ "Size down because ATR is elevated"
❌ "Only trade when trending"

These decisions require the full governance activation process.

---

## Why Volatility ≠ Trade Filter (Yet)

1. **No Empirical Validation**: We have not proven that any volatility threshold improves results.
2. **Regime Mismatch**: What worked in one regime may fail in another.
3. **Threshold Fragility**: Hard cutoffs (e.g., "skip if ATR > 2%") are often arbitrary.
4. **Curve Fitting Risk**: Optimized thresholds may not generalize.

**Rule**: Labels are observations, not filters. Use them for research analysis only.

---

## How to Interpret Results (Cautiously)

| Label | Meaning | NOT a Recommendation |
|-------|---------|----------------------|
| HIGH volatility | ATR is elevated vs history | Do NOT skip trades |
| LOW volatility | ATR is compressed vs history | Do NOT assume safety |
| TRENDING | Consistent directional moves | Do NOT assume continuation |
| RANGING | No clear direction | Do NOT assume breakout |

---

## Usage

```bash
python -m research_modules.volatility_context.cli \
    --data-path data/processed/intraday/NSE_ITC.parquet \
    --symbol ITC \
    --research-mode
```

The `--research-mode` flag is **REQUIRED**.

---

## Safety Guardrails

| Guardrail | Description |
|-----------|-------------|
| Phase Lock | Module raises `RuntimeError` if `ACTIVE_PHASE < 6`. |
| CLI Safety | `--research-mode` flag required. |
| Read-Only Output | `ContextSnapshot` is a frozen dataclass. |
| No Auto-Attach | Snapshots cannot be wired to signals automatically. |

---

## See Also

- [PHASE_LOCK.md](./PHASE_LOCK.md) - Activation requirements.
- [docs/governance/RESEARCH_MODULE_GOVERNANCE.md](../../docs/governance/RESEARCH_MODULE_GOVERNANCE.md)
