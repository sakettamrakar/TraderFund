# Project Intent

## Problem Statement
The project addresses the need for a **disciplined, observable, and scientifically rigorous trading research platform**. It aims to solve the problem of "black box" algorithmic trading by enforcing strict data lineage, glass-box observability, and validating signals through a comprehensive observation pipeline (A/B/C/D classification).

## Trading Philosophy
*   **Momentum-First**: The core edge is based on intraday momentum, utilizing VWAP, Relative Volume, and High-of-Day (HOD) proximity.
*   **Glass-Box Observation**: "Truth before Useful". The system prioritizes understanding *why* a signal was generated over raw pnl generation in the early phases.
*   **Event-Driven & Replayable**: The architecture ensures that historical replay guarantees the same behavior as live trading ("No Lookahead" bias via `CandleCursor`).

### Context Before Signal
Market Regime and Narrative Context are strictly enforced as higher-order cognitive layers. No signal or strategy is interpreted in isolation; it must exist within a valid regime and narrative structure. This is a philosophical constraint: a technically valid signal without supporting context is invalid by definition.

## Optimized Outcomes
*   **Proven Alpha**: A validated set of momentum strategies with statistically significant edge.
*   **Operational Excellence**: Zero data gaps, idempotent processing, and fully explainable signal generation.
*   **Institutional Grade Memory**: A canonical record of every signal, its validation status, and the market context.

## Non-Goals
*   **High-Frequency Trading (HFT)**: This is not a microsecond-latency arbitrage system.
*   **Black-Box AI**: We do not rely on unexplainable neural networks for core decision making; logic must be interpretable.
*   **"Get Rich Quick"**: The goal is sustainable, engineered alpha, not gambling.
*   **Universal Asset Coverage**: We focus on specific liquid markets (India Equities, US Tech via Alpha Vantage) rather than trying to trade everything.
