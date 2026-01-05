"""
##############################################################################
## PAPER TRADING ANALYTICS - READ ONLY
##############################################################################
Unit tests for analytics module.
##############################################################################
"""

import pytest
import pandas as pd
from datetime import datetime


class TestMetrics:
    """Tests for metrics calculations."""

    @pytest.fixture
    def sample_trades(self):
        """Sample trade data."""
        return pd.DataFrame({
            "timestamp": [datetime(2026, 1, 3, 10, 0), datetime(2026, 1, 3, 11, 0),
                         datetime(2026, 1, 3, 14, 0), datetime(2026, 1, 3, 15, 0)],
            "symbol": ["ITC", "HDFC", "ITC", "RELIANCE"],
            "entry_price": [100.0, 200.0, 105.0, 500.0],
            "exit_price": [105.0, 195.0, 110.0, 490.0],
            "quantity": [10, 5, 10, 2],
            "holding_minutes": [5.0, 10.0, 8.0, 15.0],
            "gross_pnl": [50.0, -25.0, 50.0, -20.0],
            "net_pnl": [50.0, -25.0, 50.0, -20.0],
            "signal_confidence": [0.8, 0.4, 0.7, 0.3],
            "signal_reason": ["momentum", "breakout", "momentum", "reversal"],
        })

    def test_execution_metrics(self, sample_trades):
        """Should calculate execution metrics correctly."""
        from paper_trading.analytics.metrics import calculate_execution_metrics

        metrics = calculate_execution_metrics(sample_trades)
        assert metrics.total_trades == 4
        assert metrics.total_symbols == 3
        assert metrics.most_traded_symbol == "ITC"
        assert metrics.most_traded_count == 2

    def test_performance_metrics(self, sample_trades):
        """Should calculate performance metrics correctly."""
        from paper_trading.analytics.metrics import calculate_performance_metrics

        metrics = calculate_performance_metrics(sample_trades)
        assert metrics.win_rate == 50.0  # 2 wins out of 4
        assert metrics.total_pnl == 55.0  # 50 - 25 + 50 - 20

    def test_empty_data(self):
        """Should handle empty data gracefully."""
        from paper_trading.analytics.metrics import calculate_execution_metrics, calculate_performance_metrics

        empty_df = pd.DataFrame()
        exec_metrics = calculate_execution_metrics(empty_df)
        perf_metrics = calculate_performance_metrics(empty_df)

        assert exec_metrics.total_trades == 0
        assert perf_metrics.win_rate == 0.0


class TestAggregations:
    """Tests for aggregation functions."""

    @pytest.fixture
    def sample_trades(self):
        return pd.DataFrame({
            "timestamp": [datetime(2026, 1, 3, 10, 0), datetime(2026, 1, 3, 13, 0),
                         datetime(2026, 1, 3, 15, 0)],
            "net_pnl": [50.0, -25.0, 30.0],
            "signal_confidence": [0.8, 0.4, 0.2],
            "signal_reason": ["momentum", "breakout", "momentum"],
        })

    def test_aggregate_by_confidence(self, sample_trades):
        """Should bucket by confidence levels."""
        from paper_trading.analytics.aggregations import aggregate_by_confidence

        buckets = aggregate_by_confidence(sample_trades)
        assert len(buckets) > 0

        # High confidence bucket should have 1 trade
        high_bucket = [b for b in buckets if "High" in b.bucket]
        assert len(high_bucket) == 1
        assert high_bucket[0].trade_count == 1

    def test_aggregate_by_time(self, sample_trades):
        """Should bucket by time of day."""
        from paper_trading.analytics.aggregations import aggregate_by_time_of_day

        buckets = aggregate_by_time_of_day(sample_trades)
        assert len(buckets) > 0


class TestDashboard:
    """Tests for dashboard generation."""

    def test_generate_summary(self):
        """Should generate summary without errors."""
        from paper_trading.analytics.dashboard import generate_summary

        df = pd.DataFrame({
            "timestamp": [datetime(2026, 1, 3, 10, 0)],
            "symbol": ["ITC"],
            "entry_price": [100.0],
            "exit_price": [105.0],
            "quantity": [10],
            "holding_minutes": [5.0],
            "gross_pnl": [50.0],
            "net_pnl": [50.0],
            "signal_confidence": [0.8],
            "signal_reason": ["momentum"],
        })

        summary = generate_summary(df)
        assert "1 trades" in summary.session_summary
        assert len(summary.positives) >= 0

    def test_empty_summary(self):
        """Should handle empty data."""
        from paper_trading.analytics.dashboard import generate_summary

        summary = generate_summary(pd.DataFrame())
        assert "No trades" in summary.session_summary


class TestSafetyGuards:
    """Tests for safety guardrails."""

    def test_phase_lock(self):
        """Should fail at wrong phase."""
        import subprocess
        from pathlib import Path

        result = subprocess.run(
            ["python", "-c",
             "import os; os.environ['TRADERFUND_ACTIVE_PHASE']='5'; "
             "from paper_trading.analytics import load_trade_logs"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent.parent),
            encoding='utf-8',
            errors='replace'
        )

        assert result.returncode != 0
        assert "PHASE LOCK" in result.stderr
