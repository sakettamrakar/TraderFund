"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Unit tests for the backtest engine.
##############################################################################
"""

import os
import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch


class TestPhaseLock:
    """Tests for the phase lock mechanism."""

    def test_engine_fails_below_phase_6(self):
        """Engine should raise RuntimeError if ACTIVE_PHASE < 6."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "5"}):
            # Need to reimport to pick up the patched env var
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            with pytest.raises(RuntimeError, match="PHASE LOCK"):
                engine_module.BacktestEngine()

    def test_engine_succeeds_at_phase_6(self):
        """Engine should initialize successfully at Phase 6+."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            engine = engine_module.BacktestEngine()
            assert engine is not None


class TestBacktestEngine:
    """Tests for the BacktestEngine class."""

    @pytest.fixture
    def engine(self):
        """Create an engine with phase lock bypassed."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)
            return engine_module.BacktestEngine(initial_capital=100000)

    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data."""
        now = datetime(2026, 1, 3, 10, 0, 0)
        data = []
        for i in range(20):
            data.append({
                "timestamp": now + timedelta(minutes=i),
                "symbol": "TEST",
                "open": 100.0 + i * 0.1,
                "high": 100.5 + i * 0.1,
                "low": 99.5 + i * 0.1,
                "close": 100.0 + i * 0.1,
                "volume": 1000 + i * 100,
            })
        return pd.DataFrame(data)

    def test_run_with_empty_data(self, engine):
        """Engine should handle empty data gracefully."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            class NoOpStrategy(engine_module.StrategyBase):
                def on_candle(self, candle, state):
                    return None

            result = engine.run(NoOpStrategy(), pd.DataFrame())
            assert result.trades == []
            assert result.final_capital == 100000

    def test_run_with_buy_sell_strategy(self, engine, sample_data):
        """Engine should execute a simple buy-sell strategy."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            class SimpleBuySell(engine_module.StrategyBase):
                def __init__(self):
                    self.count = 0

                def on_candle(self, candle, state):
                    self.count += 1
                    if self.count == 5:
                        return {"action": "BUY", "quantity": 10}
                    if self.count == 10:
                        return {"action": "SELL"}
                    return None

            result = engine.run(SimpleBuySell(), sample_data)
            assert len(result.trades) == 1
            assert result.trades[0].is_closed
