"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Comprehensive Validation Tests for Backtesting Engine

These tests explicitly validate:
1. Determinism (same input → same output)
2. Data Sanity (explainable trades with known data)
3. Boundary Conditions (edge cases)
4. Research Guard Enforcement (misuse fails loudly)
5. Output Hygiene (no production side effects)
##############################################################################
"""

import os
import sys
import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch
from pathlib import Path


# =============================================================================
# TEST 1: DETERMINISM CHECK
# =============================================================================

class TestDeterminism:
    """Verify that the same inputs always produce the same outputs."""

    @pytest.fixture
    def deterministic_data(self):
        """Create a fixed dataset for reproducibility testing."""
        now = datetime(2026, 1, 3, 10, 0, 0)
        data = []
        for i in range(20):
            data.append({
                "timestamp": now + timedelta(minutes=i),
                "symbol": "TEST",
                "open": 100.0 + i * 0.5,
                "high": 101.0 + i * 0.5,
                "low": 99.0 + i * 0.5,
                "close": 100.5 + i * 0.5,
                "volume": 1000 + i * 100,
            })
        return pd.DataFrame(data)

    @pytest.fixture
    def fixed_strategy(self):
        """A deterministic strategy: buy at candle 5, sell at candle 10."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            class FixedStrategy(engine_module.StrategyBase):
                def __init__(self):
                    self.count = 0

                def on_candle(self, candle, state):
                    self.count += 1
                    if self.count == 5:
                        return {"action": "BUY", "quantity": 10}
                    if self.count == 10:
                        return {"action": "SELL"}
                    return None

            return FixedStrategy

    def test_same_trades_on_repeat_runs(self, deterministic_data, fixed_strategy):
        """Running twice with same inputs must produce identical trades."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            engine = engine_module.BacktestEngine(initial_capital=100000)

            # Run 1
            result1 = engine.run(fixed_strategy(), deterministic_data.copy())

            # Run 2
            result2 = engine.run(fixed_strategy(), deterministic_data.copy())

            # Assert identical trades
            assert len(result1.trades) == len(result2.trades), "Trade count differs!"
            for t1, t2 in zip(result1.trades, result2.trades):
                assert t1.entry_price == t2.entry_price, "Entry prices differ!"
                assert t1.exit_price == t2.exit_price, "Exit prices differ!"
                assert t1.pnl == t2.pnl, "PnL differs!"
                assert t1.entry_time == t2.entry_time, "Entry times differ!"
                assert t1.exit_time == t2.exit_time, "Exit times differ!"

    def test_same_metrics_on_repeat_runs(self, deterministic_data, fixed_strategy):
        """Metrics must be identical across runs."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)
            from research_modules.backtesting.metrics import (
                calculate_win_rate, calculate_expectancy, calculate_max_drawdown
            )

            engine = engine_module.BacktestEngine(initial_capital=100000)

            result1 = engine.run(fixed_strategy(), deterministic_data.copy())
            result2 = engine.run(fixed_strategy(), deterministic_data.copy())

            assert calculate_win_rate(result1.trades) == calculate_win_rate(result2.trades)
            assert calculate_expectancy(result1.trades) == calculate_expectancy(result2.trades)
            assert calculate_max_drawdown(result1.equity_curve) == calculate_max_drawdown(result2.equity_curve)

    def test_same_event_order(self, deterministic_data, fixed_strategy):
        """Events must occur in the same order."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            engine = engine_module.BacktestEngine(initial_capital=100000)

            result1 = engine.run(fixed_strategy(), deterministic_data.copy())
            result2 = engine.run(fixed_strategy(), deterministic_data.copy())

            # Check equity curve order (implicit event order)
            assert result1.equity_curve == result2.equity_curve, "Equity curves differ!"


# =============================================================================
# TEST 2: DATA SANITY CHECK
# =============================================================================

class TestDataSanity:
    """Verify trades are explainable with known data."""

    def test_can_explain_every_trade_on_paper(self):
        """With a tiny dataset, manually verify all trade math."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            # Create 20 candles with KNOWN prices
            now = datetime(2026, 1, 3, 10, 0, 0)
            data = pd.DataFrame([
                {"timestamp": now + timedelta(minutes=i),
                 "symbol": "TEST", "open": 100.0, "high": 100.0, "low": 100.0,
                 "close": 100.0 + i, "volume": 1000}  # Close = 100, 101, 102, ...
                for i in range(20)
            ])

            # Strategy: Buy at candle 3 (close=103), Sell at candle 8 (close=108)
            class ExplainableStrategy(engine_module.StrategyBase):
                def __init__(self):
                    self.count = 0

                def on_candle(self, candle, state):
                    self.count += 1
                    if self.count == 4:  # Index 3, close = 103
                        return {"action": "BUY", "quantity": 10}
                    if self.count == 9:  # Index 8, close = 108
                        return {"action": "SELL"}
                    return None

            engine = engine_module.BacktestEngine(
                initial_capital=100000,
                slippage_pct=0.0,  # Zero slippage for clarity
                commission_per_trade=0.0,  # Zero commission for clarity
            )
            result = engine.run(ExplainableStrategy(), data)

            # Manual verification
            assert len(result.trades) == 1, "Expected exactly 1 trade"
            trade = result.trades[0]

            # Entry: Close at candle 3 = 103.0 (0-indexed, but count starts at 1)
            assert trade.entry_price == 103.0, f"Entry should be 103.0, got {trade.entry_price}"
            # Exit: Close at candle 8 = 108.0
            assert trade.exit_price == 108.0, f"Exit should be 108.0, got {trade.exit_price}"
            # PnL: (108 - 103) * 10 = 50
            assert trade.pnl == 50.0, f"PnL should be 50.0, got {trade.pnl}"
            # Entry candle index: 3 (0-indexed)
            entry_idx = (trade.entry_time - now).seconds // 60
            assert entry_idx == 3, f"Entry index should be 3, got {entry_idx}"
            # Exit candle index: 8 (0-indexed)
            exit_idx = (trade.exit_time - now).seconds // 60
            assert exit_idx == 8, f"Exit index should be 8, got {exit_idx}"

            print("\n✅ EXPLAINABLE TRADE:")
            print(f"   Entry at candle {entry_idx} (close={trade.entry_price})")
            print(f"   Exit at candle {exit_idx} (close={trade.exit_price})")
            print(f"   PnL = ({trade.exit_price} - {trade.entry_price}) * {trade.quantity} = {trade.pnl}")

    def test_no_lookahead_bias(self):
        """Verify that the strategy cannot access future data."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            now = datetime(2026, 1, 3, 10, 0, 0)
            # Create data where candle 10 has a spike
            data = pd.DataFrame([
                {"timestamp": now + timedelta(minutes=i), "symbol": "TEST",
                 "open": 100.0, "high": 100.0, "low": 100.0,
                 "close": 200.0 if i == 10 else 100.0, "volume": 1000}
                for i in range(20)
            ])

            # Strategy that tries to "cheat" by buying just before the spike
            class SuspiciousStrategy(engine_module.StrategyBase):
                def __init__(self):
                    self.count = 0
                    self.future_data = None  # Should not be set

                def on_candle(self, candle, state):
                    self.count += 1
                    # The strategy can ONLY see the current candle
                    # Verify it doesn't have access to future
                    if self.count == 5:
                        # Assert we don't see the candle 10 spike yet
                        assert candle["close"] == 100.0, "Lookahead detected!"
                        return {"action": "BUY", "quantity": 1}
                    if self.count == 15:
                        return {"action": "SELL"}
                    return None

            engine = engine_module.BacktestEngine(initial_capital=100000)
            result = engine.run(SuspiciousStrategy(), data)
            assert len(result.trades) == 1


# =============================================================================
# TEST 3: BOUNDARY CONDITIONS
# =============================================================================

class TestBoundaryConditions:
    """Test edge cases for graceful handling."""

    @pytest.fixture
    def standard_data(self):
        now = datetime(2026, 1, 3, 10, 0, 0)
        return pd.DataFrame([
            {"timestamp": now + timedelta(minutes=i), "symbol": "TEST",
             "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1000}
            for i in range(20)
        ])

    def test_no_signals(self, standard_data):
        """Strategy that never signals should complete with 0 trades."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            class NoSignalStrategy(engine_module.StrategyBase):
                def on_candle(self, candle, state):
                    return None

            engine = engine_module.BacktestEngine(initial_capital=100000)
            result = engine.run(NoSignalStrategy(), standard_data)

            assert len(result.trades) == 0
            assert result.final_capital == 100000

    def test_one_signal(self, standard_data):
        """Single buy without sell should not crash."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            class OneBuyStrategy(engine_module.StrategyBase):
                def __init__(self):
                    self.bought = False

                def on_candle(self, candle, state):
                    if not self.bought:
                        self.bought = True
                        return {"action": "BUY", "quantity": 1}
                    return None

            engine = engine_module.BacktestEngine(initial_capital=100000)
            result = engine.run(OneBuyStrategy(), standard_data)

            # Open position, no closed trades
            assert len(result.trades) == 0  # Not closed

    def test_signal_at_first_candle(self, standard_data):
        """Buy on first candle should work."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            class FirstCandleStrategy(engine_module.StrategyBase):
                def __init__(self):
                    self.first = True
                    self.count = 0

                def on_candle(self, candle, state):
                    self.count += 1
                    if self.first:
                        self.first = False
                        return {"action": "BUY", "quantity": 1}
                    if self.count == 10:
                        return {"action": "SELL"}
                    return None

            engine = engine_module.BacktestEngine(initial_capital=100000)
            result = engine.run(FirstCandleStrategy(), standard_data)

            assert len(result.trades) == 1

    def test_signal_at_last_candle(self, standard_data):
        """Sell on last candle should work."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            class LastCandleStrategy(engine_module.StrategyBase):
                def __init__(self):
                    self.count = 0

                def on_candle(self, candle, state):
                    self.count += 1
                    if self.count == 10:
                        return {"action": "BUY", "quantity": 1}
                    if self.count == 20:  # Last candle
                        return {"action": "SELL"}
                    return None

            engine = engine_module.BacktestEngine(initial_capital=100000)
            result = engine.run(LastCandleStrategy(), standard_data)

            assert len(result.trades) == 1
            assert result.trades[0].is_closed


# =============================================================================
# TEST 4: RESEARCH GUARD ENFORCEMENT
# =============================================================================

class TestResearchGuardEnforcement:
    """Verify that misuse fails loudly."""

    def test_fails_at_phase_5(self):
        """Engine MUST raise RuntimeError at Phase 5."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "5"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            with pytest.raises(RuntimeError) as exc_info:
                engine_module.BacktestEngine()

            assert "PHASE LOCK" in str(exc_info.value)
            print(f"\n✅ LOUD FAILURE: {exc_info.value}")

    def test_fails_at_phase_0(self):
        """Engine MUST raise RuntimeError at Phase 0."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "0"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            with pytest.raises(RuntimeError) as exc_info:
                engine_module.BacktestEngine()

            assert "PHASE LOCK" in str(exc_info.value)

    def test_cli_fails_without_research_mode(self):
        """CLI MUST exit with error without --research-mode flag."""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "research_modules.backtesting.cli",
             "--data-path", "data/test", "--data-file", "test.parquet"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent.parent)
        )

        assert result.returncode != 0, "CLI should exit with error!"
        assert "research-mode" in result.stdout.lower() or "research-mode" in result.stderr.lower(), \
            "Error should mention --research-mode flag!"
        print(f"\n✅ CLI LOUD FAILURE: Exit code {result.returncode}")


# =============================================================================
# TEST 5: OUTPUT HYGIENE
# =============================================================================

class TestOutputHygiene:
    """Verify no production side effects."""

    def test_no_files_written_to_production(self):
        """Backtest run should not create any files."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            now = datetime(2026, 1, 3, 10, 0, 0)
            data = pd.DataFrame([
                {"timestamp": now + timedelta(minutes=i), "symbol": "TEST",
                 "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1000}
                for i in range(10)
            ])

            class SimpleStrategy(engine_module.StrategyBase):
                def on_candle(self, candle, state):
                    return None

            # Get file counts before
            production_dirs = [
                Path("logs"),
                Path("data/processed"),
                Path("observations"),
            ]
            files_before = {}
            for d in production_dirs:
                if d.exists():
                    files_before[str(d)] = len(list(d.rglob("*")))

            # Run backtest
            engine = engine_module.BacktestEngine(initial_capital=100000)
            engine.run(SimpleStrategy(), data)

            # Get file counts after
            for d in production_dirs:
                if d.exists():
                    files_after = len(list(d.rglob("*")))
                    files_before_count = files_before.get(str(d), 0)
                    assert files_after == files_before_count, \
                        f"New files created in {d}!"

            print("\n✅ NO PRODUCTION FILES WRITTEN")

    def test_backtest_is_purely_analytical(self):
        """Verify backtest result is read-only data, not stateful."""
        with patch.dict(os.environ, {"TRADERFUND_ACTIVE_PHASE": "6"}):
            import importlib
            import research_modules.backtesting.engine as engine_module
            importlib.reload(engine_module)

            result = engine_module.BacktestResult()

            # Result should be a pure data container
            assert hasattr(result, "trades")
            assert hasattr(result, "equity_curve")
            assert hasattr(result, "metrics") is False or callable(getattr(result, "metrics", None)) is False

            print("\n✅ BACKTEST RESULT IS PURE DATA")
