"""
##############################################################################
## PAPER TRADING ONLY - NO REAL ORDERS
##############################################################################
Unit tests for paper trading execution.
##############################################################################
"""

import pytest
from datetime import datetime, timedelta
import tempfile
from pathlib import Path


class TestOrderSimulator:
    """Tests for order simulation."""

    def test_simulate_entry_no_slippage(self):
        """Entry without slippage should fill at requested price."""
        from paper_trading.execution.order_simulator import simulate_entry

        fill = simulate_entry("ITC", 100.0, 10, slippage_pct=0.0)
        assert fill.fill_price == 100.0
        assert fill.slippage == 0.0
        assert fill.side == "BUY"

    def test_simulate_entry_with_slippage(self):
        """Entry with slippage should fill higher (adverse)."""
        from paper_trading.execution.order_simulator import simulate_entry

        fill = simulate_entry("ITC", 100.0, 10, slippage_pct=0.5)
        assert fill.fill_price == 100.5  # 0.5% of 100 = 0.50
        assert fill.slippage == 0.5

    def test_simulate_exit_with_slippage(self):
        """Exit with slippage should fill lower (adverse)."""
        from paper_trading.execution.order_simulator import simulate_exit

        fill = simulate_exit("ITC", 100.0, 10, slippage_pct=0.5)
        assert fill.fill_price == 99.5  # Exit at lower price
        assert fill.side == "SELL"


class TestPositionTracker:
    """Tests for position tracking."""

    def test_open_position(self):
        """Should open a new position."""
        from paper_trading.execution.position_tracker import PositionTracker

        tracker = PositionTracker()
        position = tracker.open_position("ITC", 100.0, 10)

        assert tracker.has_position("ITC")
        assert position.entry_price == 100.0
        assert position.quantity == 10

    def test_cannot_open_duplicate(self):
        """Should reject duplicate position."""
        from paper_trading.execution.position_tracker import PositionTracker

        tracker = PositionTracker()
        tracker.open_position("ITC", 100.0, 10)

        with pytest.raises(ValueError):
            tracker.open_position("ITC", 105.0, 5)

    def test_close_position(self):
        """Should close an open position."""
        from paper_trading.execution.position_tracker import PositionTracker

        tracker = PositionTracker()
        tracker.open_position("ITC", 100.0, 10)
        closed = tracker.close_position("ITC", 105.0, "manual")

        assert not tracker.has_position("ITC")
        assert closed["entry_price"] == 100.0
        assert closed["exit_price"] == 105.0


class TestPnLCalculator:
    """Tests for P&L calculations."""

    def test_gross_pnl_profit(self):
        """Gross P&L for winning trade."""
        from paper_trading.execution.pnl_calculator import calculate_gross_pnl

        pnl = calculate_gross_pnl(100.0, 105.0, 10)
        assert pnl == 50.0  # (105 - 100) * 10

    def test_gross_pnl_loss(self):
        """Gross P&L for losing trade."""
        from paper_trading.execution.pnl_calculator import calculate_gross_pnl

        pnl = calculate_gross_pnl(100.0, 95.0, 10)
        assert pnl == -50.0


class TestTradeLogger:
    """Tests for trade logging."""

    def test_log_creates_file(self, tmp_path):
        """Logger should create CSV file."""
        from paper_trading.execution.trade_logger import TradeLogger

        logger = TradeLogger(log_dir=tmp_path, session_name="test")
        logger.log_trade(
            symbol="ITC",
            entry_price=100.0,
            exit_price=105.0,
            quantity=10,
            holding_minutes=5.0,
            gross_pnl=50.0,
            net_pnl=50.0,
        )

        log_files = list(tmp_path.glob("*.csv"))
        assert len(log_files) == 1

    def test_log_append_only(self, tmp_path):
        """Multiple logs should append to same file."""
        from paper_trading.execution.trade_logger import TradeLogger

        logger = TradeLogger(log_dir=tmp_path, session_name="test")
        logger.log_trade("ITC", 100, 105, 10, 5.0, 50, 50)
        logger.log_trade("HDFC", 200, 210, 5, 3.0, 50, 50)

        log_file = list(tmp_path.glob("*.csv"))[0]
        with open(log_file) as f:
            lines = f.readlines()
        assert len(lines) == 3  # Header + 2 trades


class TestSafetyGuards:
    """Tests for safety guardrails."""

    def test_phase_lock_rejects_wrong_phase(self):
        """Should fail if not in PHASE_6_PAPER."""
        import subprocess
        from pathlib import Path

        result = subprocess.run(
            ["python", "-c",
             "import os; os.environ['TRADERFUND_ACTIVE_PHASE']='5'; "
             "from paper_trading.execution import PaperTradeExecutor"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent.parent),
            encoding='utf-8',
            errors='replace'
        )

        assert result.returncode != 0
        assert "PHASE LOCK" in result.stderr

    def test_cli_rejects_without_paper_mode(self):
        """CLI should fail without --paper-mode."""
        import subprocess
        from pathlib import Path

        result = subprocess.run(
            ["python", "-m", "paper_trading.execution.cli"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent.parent),
            encoding='utf-8',
            errors='replace'
        )

        assert result.returncode != 0
        output = result.stdout + result.stderr
        assert "paper-mode" in output.lower() or "required" in output.lower()
