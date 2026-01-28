# Drawdown Governance

This module defines the **states of stress** for the portfolio and the automated responses required.

## States & Triggers

| State | Trigger (Symbolic) | Required Posture |
| :--- | :--- | :--- |
| **NORMAL** | DD < 2% | **Standard**. Evaluation as per risk envelopes. |
| **WARNING** | DD > 2% | **Defensive**. New entries **PAUSED**. Existing positions held. |
| **CRITICAL** | DD > 5% | **Reduction**. All ceilings halved. |
| **FROZEN** | DD > 10% | **Hard Stop**. All positions closed. Trading Disabled. |

## Recovery Semantics

*   **No Automatic Recovery**: Once a state escalates (e.g., NORMAL -> WARNING), it **cannot** automatically return to a lower state without manual administrative reset.
*   **Latch Mechanism**: The system latches to the highest severity state triggered during the trading session.
