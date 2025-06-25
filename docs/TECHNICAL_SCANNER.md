# Technical Scanner Module

This module implements a `TechnicalScanner` class for generating trading signals based on common technical indicators.  The scanner evaluates OHLCV data and combines multiple indicators to produce a JSON alert describing the overall market bias.

## Implemented Indicators

- **EMA12/EMA26 Crossover** with volume confirmation (volume greater than 1.2× the 20-period average).
- **SMA50/SMA200 Cross** for golden and death cross detection.
- **Ichimoku Cloud** Tenkan/Kijun cross with price relative to the cloud.
- **VWAP** trend indication for intraday data.
- **Stochastic RSI (14,3,3)** for overbought/oversold signals.
- **MACD (12,26,9)** line and signal crossovers.
- **Pivot Point** support/resistance confirmation.

The module aggregates the indicators and outputs a JSON object containing:

```
{
  "signal": "bullish" | "bearish" | "neutral",
  "strength": 0-100,
  "confirmations": <number of confirming indicators>,
  "indicators": [ {"indicator": "EMA12/26", "signal": "bullish"}, ... ]
}
```

Strength is calculated as the ratio of confirming indicators to total detected indicators, scaled to 0–100.
