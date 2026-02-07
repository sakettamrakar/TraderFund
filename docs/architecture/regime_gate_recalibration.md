# Regime Gate Recalibration

## 1. Philosophy
The Regime Gate determine "Permission to Engage".
*   **BULLISH**: All systems go.
*   **NEUTRAL**: Selective engagement (Mean Reversion only).
*   **BEARISH**: Capital Preservation (Cash / Short).

With richer data, we move from "Price-Only" gating to "Multi-Factor" gating.

---

## 2. United States (US) Gate Logic

### 2.1. The "Green" Gate (BULLISH)
**Condition**:
1.  **Price**: `Composite(SPY+QQQ)` > SMA50.
2.  **Vol**: `VIX` < 25.
3.  **Macro**: `10Y Yield` Trend != "Parabolic Spike".

*Change*: Previously only looked at SPY price. Now, a VIX spike (>25) can veto a Bullish regime even if Price is high (Data Integrity/Fear veto).

### 2.2. The "Yellow" Gate (NEUTRAL)
**Condition**:
1.  **Price**: Mixed (e.g., SPY > SMA50 but QQQ < SMA50).
2.  *OR* **Vol**: `VIX` is elevated (20-30) but Price is holding.

*Change*: Captures the "Rotation" phase where Tech dumps but Value holds up.

### 2.3. The "Red" Gate (BEARISH)
**Condition**:
1.  **Price**: `Composite` < SMA200.
2.  *OR* **Vol**: `VIX` > 30 (Panic).

---

## 3. India (IN) Gate Logic (Surrogate Constrained)

### 3.1. The "Green" Gate (BULLISH)
**Condition**:
1.  **Price**: `RELIANCE` > SMA50.
2.  **Vol**: `RealizedVol(20d)` < 75th Percentile of History.

### 3.2. The "Red" Gate (BEARISH)
**Condition**:
1.  **Price**: `RELIANCE` < SMA200.

**Governance Note**: The "India Gate" is inherently "Stock Specific". If Reliance crashes due to corporate news, the entire India system shuts down. This is an unavoidable artifact of the current data gap, but it is **SAFER** than having no gate.

---

## 4. Recalibration Execution
1.  **Backtest**: Run the new Gate Logic against the last 365 days of `data_provenance_US`.
2.  **Verify**: Ensure it doesn't flip-flop everyday (hysteresis required).
3.  **Apply**: Hard-code the new thresholds into `regime_manager.py`.
