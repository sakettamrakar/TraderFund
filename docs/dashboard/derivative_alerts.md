# Derivative Alerts (State Transition Detection)

**Version**: 1.0
**Date**: 2026-01-29

## Objective
To answer the question: *"Did something just change?"*

## Definition
A derivative alert is a read-only notification generated when the first derivative of the state (change over discrete time) is non-zero.

$$ \Delta S = S(t) \neq S(t-1) $$

## Scope
Alerts are generated for:
- **Momentum**: `NONE` $\leftrightarrow$ `EMERGING`
- **Expansion**: `NONE` $\leftrightarrow$ `EARLY`
- **Dispersion**: `NONE` $\leftrightarrow$ `BREAKOUT`
- **Liquidity**: `NEUTRAL` $\leftrightarrow$ `COMPRESSED`

## Presentation
- **Location**: Top of "Market Structure Snapshot" panel.
- **Style**: Amber/Warning coloration for visibility.
- **Content**: "Momentum Changed: NONE -> EMERGING"
- **Persistence**: Ephemeral (exists only while the latest tick represents the change).

## Safety
- **No triggers**: Alerts are purely informational. They do not trigger automated trading.
- **No acknowledgement**: Alerts do not require operator dismissal (they clear on next tick if state stabilizes).
