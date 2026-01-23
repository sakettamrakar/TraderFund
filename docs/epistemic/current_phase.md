# Current Lifecycle Phase

## Phase Definition: Research & Validation (Shadow Mode)

The project is currently in the **Research & Validation** phase. We are transitioning from pure backtesting/replay into **"Live Shadow Mode"**.

## Phase Stability Rule
During the current phase, core cognitive layers (Genesis, Regime, Accumulation) are considered **frozen**. Any structural changes to these layers require an explicit research hypothesis and formal validation. We prioritize stability of the observation lens over optimization of the view.

## In Scope
*   **Data Ingestion**: Robust WebSocket ingestion for India (Angel One) and REST polling for US (Alpha Vantage).
*   **Signal Generation**: V0 Momentum Strategy execution (VWAP, Rel Vol, HOD).
*   **Observation**: Automated daily logging of signals, "Clinical Review" by humans, and automated performance tracking (T+5, T+15).
*   **Infrastructure**: Local orchestration, basic dashboarding (Glass-box), and Historical Replay for diagnostics.
*   **Documentation**: Epistemic grounding and architectural documentation.

## Out of Scope (For Now)
*   **Automated Live Execution**: No live money orders are sent automatically.
*   **Portfolio Optimization**: Advanced position sizing, covariance matrices, and risk parity models are not currently active.
*   **Complex Derivatives**: Focus is primarily on the momentum of liquid underlying assets or simple implementations.
*   **External Investor Reporting**: The current output is for internal research metrics only.

## Entry Criteria
*   Pipeline is capable of end-to-end execution (Ingest -> Process -> Signal -> Log).
*   Data sources are stable and configured.

## Exit Criteria
*   **Stability**: Zero "Orphans" (data gaps) and zero critical crashes for a sustained period (e.g., 2 weeks).
*   **Validation**: Consistent generation of "A" or "B" grade signals in Shadow Mode as verified by the Observation module.
*   **Idempotency**: Live signals match Historical Replay signals 100% for the same data period.
