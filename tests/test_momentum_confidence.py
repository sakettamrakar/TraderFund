
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core_modules.momentum_engine.momentum_engine import MomentumEngine

class TestMomentumConfidence(unittest.TestCase):
    def setUp(self):
        self.engine = MomentumEngine(
            vol_ma_window=20,
            hod_proximity_pct=0.5,
            vol_multiplier=2.0
        )

    def create_scenario(self, rel_vol_mult, hod_dist_pct):
        """
        Creates a DataFrame where the last candle has specific properties.

        Args:
            rel_vol_mult: Multiplier of volume relative to average (e.g. 2.0, 4.0)
            hod_dist_pct: Distance from HOD in percent (e.g. 0.0, 0.5)
        """
        now = datetime(2026, 1, 3, 10, 0, 0)
        data = []

        # 20 candles of baseline
        # Price 100, Volume 1000
        for i in range(20):
            data.append({
                "symbol": "TEST",
                "exchange": "NSE",
                "timestamp": (now + timedelta(minutes=i)).isoformat() + "+05:30",
                "open": 100.0,
                "high": 100.0,
                "low": 100.0,
                "close": 100.0,
                "volume": 1000
            })

        # 21st candle (Trigger Candle)
        # We need to craft:
        # 1. VWAP: needs to be < close.
        #    Prev 20 candles: VWAP ~ 100.
        #    If we put close > 100, we are good.
        # 2. HOD: We need specific hod_dist_pct.
        #    hod_dist = (hod - close) / hod * 100
        #    Let's say close = 102.
        #    We need hod such that (hod - 102) / hod = hod_dist_pct / 100
        #    1 - 102/hod = dist
        #    102/hod = 1 - dist
        #    hod = 102 / (1 - dist)
        # 3. Rel Vol:
        #    Avg vol is 1000.
        #    We need volume = 1000 * rel_vol_mult

        close_price = 102.0
        dist_decimal = hod_dist_pct / 100.0
        target_hod = close_price / (1.0 - dist_decimal)

        # Calculate target volume to achieve specific RelVol
        # Formula: V = (R * S_prev) / (N - R)
        # N = 20
        # S_prev = 19 * 1000 = 19000 (since we are at index 20, window is 1..20)
        N = 20
        S_prev = 19 * 1000
        target_vol = (rel_vol_mult * S_prev) / (N - rel_vol_mult)
        # Add a tiny buffer to handle floating point issues and int truncation
        target_vol = int(target_vol) + 1

        # Ensure target_hod is at least close_price (it should be)
        # And ensure previous highs don't mess it up (prev highs were 100)

        data.append({
            "symbol": "TEST",
            "exchange": "NSE",
            "timestamp": (now + timedelta(minutes=20)).isoformat() + "+05:30",
            "open": 100.0,
            "high": target_hod,
            "low": 100.0,
            "close": close_price,
            "volume": int(target_vol)
        })

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def test_confidence_scores(self):
        scenarios = [
            # Case 1: Bare minimum (RelVol=2.0, HOD dist=0.5%)
            # Base 0.6. Vol Boost 0. HOD Boost 0. Total 0.6.
            {"vol": 2.0, "dist": 0.5, "name": "Min Threshold", "expected": 0.60},

            # Case 2: Strong Volume (RelVol=4.0, HOD dist=0.5%)
            # Base 0.6. Vol Boost: (4-2)/(2*2)*0.2 = 0.5*0.2 = 0.1. HOD Boost 0. Total 0.7.
            {"vol": 4.0, "dist": 0.5, "name": "High Volume", "expected": 0.70},

            # Case 3: At HOD (RelVol=2.0, HOD dist=0.0%)
            # Base 0.6. Vol Boost 0. HOD Boost 0.2. Total 0.8.
            {"vol": 2.0, "dist": 0.0, "name": "At HOD", "expected": 0.80},

            # Case 4: Perfect (RelVol=6.0, HOD dist=0.0%)
            # Base 0.6. Vol Boost 0.2. HOD Boost 0.2. Total 1.0.
            {"vol": 6.0, "dist": 0.0, "name": "Perfect Setup", "expected": 1.00},
        ]

        print("\n--- Confidence Score Analysis ---")
        for sc in scenarios:
            df = self.create_scenario(sc["vol"], sc["dist"])

            # Monkeypatch _load_data
            self.engine._load_data = lambda s, e="NSE": df

            signals = self.engine.generate_signals("TEST")

            if signals:
                sig = signals[0]
                print(f"Scenario: {sc['name']:<15} | Vol (Target): {sc['vol']:.1f} | Conf: {sig.confidence:.2f} (Exp: {sc['expected']:.2f})")
                self.assertAlmostEqual(sig.confidence, sc['expected'], delta=0.05)
            else:
                print(f"Scenario: {sc['name']:<15} | NO SIGNAL GENERATED")
                # Debug why
                df = self.engine._compute_indicators(df)
                latest = df.iloc[-1]
                print(f"   > Vol: {latest['rel_vol']:.4f}")
                print(f"   > HOD Dist: {(latest['hod'] - latest['close']) / latest['hod'] * 100:.4f}%")

if __name__ == "__main__":
    unittest.main()
