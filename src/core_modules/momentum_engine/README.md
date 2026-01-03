# Momentum Engine (v0)

A minimal, production-safe momentum engine for TraderFund.

## Features
- **VWAP Alignment**: Only generates long signals when price is above intraday VWAP.
- **HOD Proximity**: Identifies breakout potential when price is within $0.5\%$ of the daily high.
- **Relative Volume**: Detects institutional interest when volume exceeds $2x$ the moving average.

## Usage
The engine consumes processed intraday Parquet data.

```python
from src.core_modules.momentum_engine.momentum_engine import MomentumEngine

engine = MomentumEngine()
signals = engine.run_on_all(["RELIANCE", "TCS"])
```

## Signal Logic
A `MOMENTUM_LONG` signal is generated if:
1. `close > vwap`
2. `(hod - close) / hod <= 0.005`
3. `volume / volume_avg >= 2.0`

## Output Format
Signals are structured objects containing symbol, timestamp, confidence, and hints for entry/stop.
