
import pytest
import os
import json
import pandas as pd
from datetime import datetime
from traderfund.regime.shadow import ShadowRegimeRunner
from traderfund.regime.analytics import RegimeAnalytics
from traderfund.regime.types import MarketBehavior

class TestShadowMode:
    TEST_LOG = "test_shadow.jsonl"
    
    @classmethod
    def setup_class(cls):
        # Clean up previous runs
        if os.path.exists(cls.TEST_LOG):
            os.remove(cls.TEST_LOG)

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.TEST_LOG):
            os.remove(cls.TEST_LOG)

    @pytest.fixture
    def mock_market_data(self):
        # Create a tiny DF to pass validation
        return pd.DataFrame({
            'high': [100, 101, 102] * 20,
            'low': [99, 100, 101] * 20,
            'close': [100.5, 100.5, 101.5] * 20, # Low volatility
            'volume': [1000] * 60,
            'timestamp': pd.date_range("2024-01-01", periods=60, freq="1min")
        })

    def test_runner_execution(self, mock_market_data):
        runner = ShadowRegimeRunner(log_file_path=self.TEST_LOG, enabled=True)
        
        # Run a tick
        state = runner.on_tick(mock_market_data, "TEST_SYM")
        
        # Verify state computed
        assert state is not None
        assert state.behavior in MarketBehavior
        
        # Verify Log File created and populated
        assert os.path.exists(self.TEST_LOG)
        
        runner.close() # Release handle
        
        with open(self.TEST_LOG, 'r') as f:
            lines = f.readlines()
            assert len(lines) >= 1
            last_line = json.loads(lines[-1])
            
            # Verify Shadow Fields
            assert 'shadow' in last_line
            assert 'would_block' in last_line['shadow']
            assert isinstance(last_line['shadow']['would_block'], list)

    def test_analytics_parsing(self):
        # 1. Create dummy log
        data = [
            {"regime": {"behavior": "TRENDING_NORMAL_VOL"}, "shadow": {"would_block": []}},
            {"regime": {"behavior": "EVENT_LOCK"}, "shadow": {"would_block": ["MOMENTUM", "MEAN_REVERSION"]}},
            {"regime": {"behavior": "EVENT_LOCK"}, "shadow": {"would_block": ["MOMENTUM", "MEAN_REVERSION"]}}
        ]
        
        with open(self.TEST_LOG, 'w') as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")
                
        # 2. Parse
        metrics = RegimeAnalytics.compute_metrics(RegimeAnalytics.load_telemetry(self.TEST_LOG))
        
        assert metrics['total_ticks'] == 3
        assert metrics['total_transitions'] == 1 # Normal -> Lock
        assert metrics['regime_distribution_pct']['EVENT_LOCK'] > 60.0
        assert metrics['strategy_block_rate_pct']['MOMENTUM'] > 60.0

    def test_disabled_mode(self, mock_market_data):
        runner = ShadowRegimeRunner(log_file_path=self.TEST_LOG, enabled=False)
        state = runner.on_tick(mock_market_data, "TEST_SYM")
        assert state is None
        runner.close()
