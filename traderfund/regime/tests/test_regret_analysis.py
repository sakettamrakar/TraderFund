
import pytest
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from traderfund.regime.regret_analysis import RegimeRegretAnalyzer

class TestRegimeRegretAnalysis:
    REGIME_LOG = "test_regime_log.jsonl"
    SIGNAL_LOG = "test_signal_log.csv"
    OUTCOME_LOG = "test_outcome_log.csv"

    @classmethod
    def setup_class(cls):
        # 1. Create Regime Log (Shadow)
        # Sequence: Normal -> Event Lock -> Normal
        base_time = datetime(2024, 1, 1, 10, 0, 0)
        regime_data = [
            # T=0: Normal
            {
                "meta": {"timestamp": base_time.isoformat(), "symbol": "INFY"},
                "regime": {"behavior": "TRENDING_NORMAL_VOL"},
                "shadow": {"would_block": []}
            },
            # T=10s: Lock
            {
                "meta": {"timestamp": (base_time + timedelta(seconds=10)).isoformat(), "symbol": "INFY"},
                "regime": {"behavior": "EVENT_LOCK"},
                "shadow": {"would_block": ["MOMENTUM"]}
            },
            # T=20s: Normal
            {
                "meta": {"timestamp": (base_time + timedelta(seconds=20)).isoformat(), "symbol": "INFY"},
                "regime": {"behavior": "TRENDING_NORMAL_VOL"},
                "shadow": {"would_block": []}
            }
        ]
        with open(cls.REGIME_LOG, 'w') as f:
            for entry in regime_data:
                f.write(json.dumps(entry) + "\n")

        # 2. Create Signal Log
        # Sig1: T=2s (Normal) -> Not Blocked
        # Sig2: T=12s (Lock) -> Blocked
        signals = pd.DataFrame({
            'timestamp': [
                base_time + timedelta(seconds=2),
                base_time + timedelta(seconds=12)
            ],
            'symbol': ['INFY', 'INFY'],
            'strategy': ['MOMENTUM', 'MOMENTUM'],
            'signal_id': ['S1', 'S2']
        })
        signals.to_csv(cls.SIGNAL_LOG, index=False)

        # 3. Create Outcome Log
        # S1: PnL +100 (Executed, so hypothetical logic doesn't matter much for regret, but good for base)
        # S2: PnL -50 (This trade WOULD have lost money if taken. Blocking it saved 50.)
        outcomes = pd.DataFrame({
            'signal_id': ['S1', 'S2'],
            'pnl': [100.0, -50.0]
        })
        outcomes.to_csv(cls.OUTCOME_LOG, index=False)

    @classmethod
    def teardown_class(cls):
        for f in [cls.REGIME_LOG, cls.SIGNAL_LOG, cls.OUTCOME_LOG]:
            if os.path.exists(f):
                os.remove(f)

    def test_analysis_pipeline(self):
        analyzer = RegimeRegretAnalyzer(tolerance_seconds=5)
        
        # 1. Load & Join
        df = analyzer.load_data(self.REGIME_LOG, self.SIGNAL_LOG, self.OUTCOME_LOG)
        
        assert not df.empty
        assert len(df) == 2
        
        # Verify timestamps aligned correctly
        # S1 (2s) should match T=0 Regime (Normal)
        row1 = df.iloc[0]
        assert row1['behavior'] == "TRENDING_NORMAL_VOL"
        assert row1['signal_id'] == "S1"
        
        # S2 (12s) should match T=10s Regime (Lock)
        row2 = df.iloc[1]
        assert row2['behavior'] == "EVENT_LOCK"
        assert row2['signal_id'] == "S2"
        assert "MOMENTUM" in row2['blocked_strategies']

    def test_regret_computation(self):
        analyzer = RegimeRegretAnalyzer()
        df = analyzer.load_data(self.REGIME_LOG, self.SIGNAL_LOG, self.OUTCOME_LOG)
        
        regret = analyzer.compute_regret(df)
        
        assert not regret.empty
        
        # We expect 2 rows: one for Normal, one for Lock
        
        # Row 1: Normal
        normal_row = regret[regret['regime_behavior'] == "TRENDING_NORMAL_VOL"].iloc[0]
        assert normal_row['block_rate'] == 0.0
        assert normal_row['blocked_pnl'] == 0.0
        
        # Row 2: Lock
        lock_row = regret[regret['regime_behavior'] == "EVENT_LOCK"].iloc[0]
        assert lock_row['block_rate'] == 100.0
        assert lock_row['blocked_pnl'] == -50.0 # We blocked a loss
        assert lock_row['prevented_loss'] == 50.0
        assert lock_row['regret_score'] == 50.0 # Positive score = Good blocking

    def test_scorecard_generation(self):
        analyzer = RegimeRegretAnalyzer()
        df = analyzer.load_data(self.REGIME_LOG, self.SIGNAL_LOG, self.OUTCOME_LOG)
        regret = analyzer.compute_regret(df)
        card = analyzer.generate_scorecard(regret)
        
        assert "REGIME ENGINE REGRET ANALYSIS SCORECARD" in card
        assert "NET REGRET SCORE: +50.00" in card
        assert "EVENT_LOCK" in card
