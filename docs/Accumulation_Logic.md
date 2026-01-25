# Accumulation Logic

**Status:** APPROVED
**Last Updated:** 2026-01-17

## 1. Purpose

Capture **slow-burn narratives** that emerge from multiple weak signals over time, without lowering the main Genesis threshold.

## 2. How It Works

### Buffer
- LOW severity events are stored in an in-memory buffer.
- Events are keyed by their `semantic_tag` (e.g., "SUPPLY_CHAIN", "RATES").
- Buffer retains events for a **rolling window of 48 hours**.

### Promotion Rule
When **3 or more LOW events** share the same `semantic_tag` within the window:
1.  A **SYNTHETIC_MEDIUM** event is created with `severity = 65.0`.
2.  The synthetic event flows into Genesis normally.
3.  The synthetic event is marked with `accumulated: True`.

### Original Events
- Original LOW events are **never mutated**.
- They remain in the buffer until they expire (window elapses).

## 3. Example

```
Event 1: "Chip shortage worsens in Asia" (LOW, tag: SUPPLY_CHAIN, T=0h)
Event 2: "Taiwan fab delays reported" (LOW, tag: SUPPLY_CHAIN, T=12h)
Event 3: "Auto sector cites chip constraints" (LOW, tag: SUPPLY_CHAIN, T=24h)

→ PROMOTION TRIGGERED
→ Synthetic Event: "SUPPLY_CHAIN accumulation (3 events)" (MEDIUM, severity=65)
→ Genesis accepts synthetic event (65 > 60 threshold)
→ Regime dampens final weight
```

## 4. Explicit Non-Goals

1.  **No Text Analysis:** Accumulation uses semantic tags assigned upstream, not NLP.
2.  **No Regime Logic:** Accumulation is severity-based only. Regime dampening happens later.
3.  **No Prediction:** Accumulation does not predict impact or direction.
4.  **No Auto-Tuning:** The "3 events" threshold is a fixed constant.
