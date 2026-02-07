# System Discontinuity Log

## 1. Purpose
To record expected "jumps" or "shifts" in system behavior resulting from the `PROXY_IGNITION` task. These are features, not bugs, but will look like anomalies in long-term time-series charts.

---

## 2. Log of Discontinuities

### [DSC-001] US Momentum Shift
*   **Scope**: US Market / Momentum Factor.
*   **Description**: Introduction of QQQ (Nasdaq 100) into the momentum composite.
*   **Effect**: Momentum score will become more volatile and "tech-sensitive".
*   **Expected Jump**: usage of QQQ may cause the momentum score to diverge from the "Pure SPY" history by +/- 15%.
*   **Mitigation**: None. This is a correction to reality. Annotate charts on change date.

### [DSC-002] US Volatility Scale Change
*   **Scope**: US Market / Volatility Factor.
*   **Description**: Switching from `StdDev(Price)` to `VIX`.
*   **Effect**: The units will change completely.
    *   Old: ~0.015 (Daily Returns SD).
    *   New: ~15.0 (VIX Index).
*   **Mitigation**: Normalization layer must divide VIX by appropriate scaling factor to map to [0,1] confidence interval for the Factor Engine.

### [DSC-003] India "Single Point of Failure" Explicit
*   **Scope**: India Market / All Factors.
*   **Description**: Formal designation of RELIANCE as Surrogate.
*   **Effect**: System is now explicitly coupled to one stock's idiosyncrasies.
*   **Risk**: Earnings disconnects (Stock falls on bad earnings while Market is up).
*   **Mitigation**: **Human-in-the-loop** monitoring required for India until Nifty Index data is wired.

### [DSC-004] Gap Visibility
*   **Scope**: Dashboard.
*   **Description**: Dashboard will now likely show "N/A" or "Gap" for breadth and credit factors that were previously just assumed "Normal" or ignored.
*   **Effect**: "Health" scores might drop because of missing data coverage.
*   **Rationale**: Better to show "Unknown" than "False Good".

---

## 3. Sign-Off
*   **Acceptance**: The Project Lead acknowledges these discontinuities are necessary for Epistemic Honesty.
