# Selective Pipeline Activation Controller - Design & Architecture

## Overview
The **Selective Pipeline Activation Controller** is the intelligence layer that minimizes redundant computation by justifying the execution of every stage for every symbol. It ensures the system scales efficiently by running analysis only when specific "activation conditions" are met.

## Core Principles
1. **Justified Execution**: No stage runs without a valid trigger (interval or score/state threshold).
2. **Cascading Activation**: Success in early stages (Structural, Energy) "unlocks" later stages (Momentum, Risk).
3. **Budget Consciousness**: Avoids re-processing static data by tracking `last_run` timestamps.
4. **Deterministic Decisions**: Rules are hard-coded in `config.py`, ensuring transparency.

## Activation Eligibility Rules

| Stage | Trigger Condition | Rationale |
| :--- | :--- | :--- |
| **S0: Hygiene** | Every 7 days | Maintain universe quality without daily churn. |
| **S1: Structural** | Every 3 days AND history loaded | Update health profile regularly once data is available. |
| **S2: Energy** | S1 Score >= 50.0 | Only analyze energy on symbols that show structural fitness. |
| **S3: Participation** | S2 State in [`forming`, `mature`] | Focus on symbols where stored energy is ready to release. |
| **S4: Momentum** | S3 State in [`emerging`, `active`] | Confirm momentum only when participation validates the move. |
| **S5: Risk** | S4 State in [`emerging`, `confirmed`] | Profile risk only for symbols exhibiting active momentum. |

## Controller Components
- **`config.py`**: Houses the thresholds and intervals.
- **`models.py`**: Defines `ActivationDecision` (the plan) and `SymbolState` (the history).
- **`controller.py`**: Implements the decision logic, cross-referencing previous results.
- **`runner.py`**: The orchestrator that generates the plan and invokes the stage modules.

## Example Activation Plans

### AAPL (Steady State)
- **Status**: Structural score 73, Energy none.
- **Decision**: Run S0, S1 (interval), S2. Skip S3-S5.
- **Reason**: S2 state is `none`, meaning no participation check is required.

### GOOGL (Active Momentum)
- **Status**: S1: 75, S2: `mature`, S3: `active`, S4: `confirmed`.
- **Decision**: Run S1-S5.
- **Reason**: All prerequisite conditions met; risk profiling (S5) is critical.

### MSFT (Early Stage)
- **Status**: S1: 72, S2: `forming`, S3: `emerging`, S4: `none`.
- **Decision**: Run S1-S4.
- **Reason**: Participation detected (S3), triggering a momentum check (S4).

## Execution History
Tracked in `data/controller/us/execution_history.parquet`. Ensures resume-safe and idempotent operations.
