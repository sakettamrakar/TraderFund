# Decision Policy Epistemic Rationale

## 1. The Separation of Truth and Action
In many trading systems, "Signal" and "Action" are conflated. A Moving Average Crossover is treated as a "Buy Signal".
In TraderFund, we enforce a strict separation:
1.  **Truth**: Moving Average Crossed Over (Objective Fact).
2.  **Meaning**: Momentum is Positive (Interpretation).
3.  **Policy**: Buying is Permitted (Governance).
4.  **Action**: Buy Symbol X (Execution).

## 2. Why this Layer Exists
This layer protects the system from **Epistemic Overreach**.
A strategy might find a brilliant "Buy" setup in `NIFTY`, but if the Governance layer knows that `NIFTY` data is actually a Proxy Surrogate (`RELIANCE`) with degraded integrity, the **Policy Layer** must intervene and block the action.
The Strategy is "Smart" but "Blind" to the systemic health. The Policy is the "Health & Safety Officer".

## 3. The "Constraint-First" Philosophy
We do not ask "What should we do?". We ask "What are we **allowed** to do?".
By default, the answer is `NOTHING`.
We must *accumulate permissions* from valid truth states.
*   Is Data Valid? (+Permission to Observe)
*   Is Regime Constructive? (+Permission to Hold)
*   Is Opportunity High? (+Permission to Enter)

## 4. India Surrogate Rationale
For Phase 10, India uses a Single-Stock Surrogate. Mathematically, this is insufficient to characterize Market Beta or Sector Rotation.
Therefore, the **Epistemic Rationale** demands that while we can *calculate* factors (for research), we strictly **forbid** capital allocation (trading) because the basis of truth is known to be flawed.
The Policy Layer is where this prohibition is encoded ("If Proxy=DEGRADED then Block=ENTRY").
