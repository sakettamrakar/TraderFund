from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class TechnicalScanner:
    """Scanner for generating technical analysis signals."""

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return DataFrame with all required technical indicators."""
        df = df.copy()

        # Exponential Moving Averages
        df["ema_12"] = df["close"].ewm(span=12, adjust=False).mean()
        df["ema_26"] = df["close"].ewm(span=26, adjust=False).mean()

        # Simple Moving Averages
        df["sma_50"] = df["close"].rolling(window=50).mean()
        df["sma_200"] = df["close"].rolling(window=200).mean()

        # Ichimoku Components
        high = df["high"]
        low = df["low"]
        df["tenkan"] = (high.rolling(9).max() + low.rolling(9).min()) / 2
        df["kijun"] = (high.rolling(26).max() + low.rolling(26).min()) / 2
        df["senkou_span_a"] = ((df["tenkan"] + df["kijun"]) / 2).shift(26)
        df["senkou_span_b"] = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(
            26
        )

        # Volume Weighted Average Price
        df["vwap"] = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()

        # Relative Strength Index
        delta = df["close"].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = up.rolling(14).mean()
        roll_down = down.rolling(14).mean()
        rs = roll_up / roll_down
        df["rsi"] = 100 - 100 / (1 + rs)

        # Stochastic RSI (14,3,3)
        min_rsi = df["rsi"].rolling(14).min()
        max_rsi = df["rsi"].rolling(14).max()
        stoch_rsi = (df["rsi"] - min_rsi) / (max_rsi - min_rsi)
        df["stoch_rsi_k"] = stoch_rsi.rolling(3).mean()
        df["stoch_rsi_d"] = df["stoch_rsi_k"].rolling(3).mean()

        # MACD
        df["macd"] = df["ema_12"] - df["ema_26"]
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        return df

    def scan_for_signals(self, ohlcv_data: pd.DataFrame) -> str:
        """Scan OHLCV data and return a JSON string of detected signals."""
        df = self.compute_indicators(ohlcv_data)
        signals = []

        def crossed_above(s1: pd.Series, s2: pd.Series) -> bool:
            return s1.iloc[-2] < s2.iloc[-2] and s1.iloc[-1] > s2.iloc[-1]

        def crossed_below(s1: pd.Series, s2: pd.Series) -> bool:
            return s1.iloc[-2] > s2.iloc[-2] and s1.iloc[-1] < s2.iloc[-1]

        vol_confirm = df["volume"].iloc[-1] > 1.2 * df["volume"].rolling(20).mean().iloc[-1]

        # EMA 12/26 crossover
        if crossed_above(df["ema_12"], df["ema_26"]) and vol_confirm:
            signals.append({"indicator": "EMA12/26", "signal": "bullish"})
        elif crossed_below(df["ema_12"], df["ema_26"]) and vol_confirm:
            signals.append({"indicator": "EMA12/26", "signal": "bearish"})

        # SMA 50/200 cross
        if crossed_above(df["sma_50"], df["sma_200"]):
            signals.append({"indicator": "SMA50/200", "signal": "bullish"})
        elif crossed_below(df["sma_50"], df["sma_200"]):
            signals.append({"indicator": "SMA50/200", "signal": "bearish"})

        # Ichimoku signals
        close = df["close"].iloc[-1]
        cloud_top = max(df["senkou_span_a"].iloc[-1], df["senkou_span_b"].iloc[-1])
        cloud_bottom = min(df["senkou_span_a"].iloc[-1], df["senkou_span_b"].iloc[-1])
        if crossed_above(df["tenkan"], df["kijun"]) and close > cloud_top:
            signals.append({"indicator": "Ichimoku", "signal": "bullish"})
        elif crossed_below(df["tenkan"], df["kijun"]) and close < cloud_bottom:
            signals.append({"indicator": "Ichimoku", "signal": "bearish"})

        # VWAP
        if close > df["vwap"].iloc[-1]:
            signals.append({"indicator": "VWAP", "signal": "bullish"})
        elif close < df["vwap"].iloc[-1]:
            signals.append({"indicator": "VWAP", "signal": "bearish"})

        # Stochastic RSI
        if crossed_above(df["stoch_rsi_k"], df["stoch_rsi_d"]) and df["stoch_rsi_k"].iloc[-1] < 0.2:
            signals.append({"indicator": "StochRSI", "signal": "bullish"})
        elif crossed_below(df["stoch_rsi_k"], df["stoch_rsi_d"]) and df["stoch_rsi_k"].iloc[-1] > 0.8:
            signals.append({"indicator": "StochRSI", "signal": "bearish"})

        # MACD
        if crossed_above(df["macd"], df["macd_signal"]):
            signals.append({"indicator": "MACD", "signal": "bullish"})
        elif crossed_below(df["macd"], df["macd_signal"]):
            signals.append({"indicator": "MACD", "signal": "bearish"})

        # Pivot point confirmation
        pivot = (df["high"].iloc[-1] + df["low"].iloc[-1] + df["close"].iloc[-1]) / 3
        resistance1 = 2 * pivot - df["low"].iloc[-1]
        support1 = 2 * pivot - df["high"].iloc[-1]
        pivot_signal = None
        if close > resistance1:
            pivot_signal = "bullish"
        elif close < support1:
            pivot_signal = "bearish"
        if pivot_signal:
            signals.append({"indicator": "Pivot", "signal": pivot_signal})

        if not signals:
            return json.dumps({
                "signal": "neutral",
                "strength": 0,
                "confirmations": 0,
                "indicators": [],
            })

        counts = {"bullish": 0, "bearish": 0}
        for s in signals:
            counts[s["signal"]] += 1

        if counts["bullish"] > counts["bearish"]:
            final_signal = "bullish"
            confirmations = counts["bullish"]
        elif counts["bearish"] > counts["bullish"]:
            final_signal = "bearish"
            confirmations = counts["bearish"]
        else:
            final_signal = "neutral"
            confirmations = counts["bullish"]

        strength = int(confirmations / len(signals) * 100)

        return json.dumps(
            {
                "signal": final_signal,
                "strength": strength,
                "confirmations": confirmations,
                "indicators": signals,
            },
            indent=2,
        )
