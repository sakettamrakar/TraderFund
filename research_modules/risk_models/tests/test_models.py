"""
##############################################################################
## RESEARCH ONLY - NOT FOR LIVE TRADING
##############################################################################
Unit tests for risk models.
##############################################################################
"""

import pytest


class TestFixedRisk:
    """Tests for fixed fractional risk model."""

    def test_position_size_calculation(self):
        """Position size should be risk amount / stop distance."""
        from research_modules.risk_models.models.fixed_risk import calculate_position_size
        # Capital = 100000, Risk = 1%, Entry = 100, Stop = 95
        # Risk Amount = 1000, Stop Distance = 5
        # Position Size = 1000 / 5 = 200
        size = calculate_position_size(100000, 1.0, 100, 95)
        assert size == 200

    def test_position_size_with_zero_stop(self):
        """Should return 0 if stop distance is 0."""
        from research_modules.risk_models.models.fixed_risk import calculate_position_size
        size = calculate_position_size(100000, 1.0, 100, 100)
        assert size == 0

    def test_risk_amount_calculation(self):
        """Risk amount should be capital * risk_pct / 100."""
        from research_modules.risk_models.models.fixed_risk import calculate_risk_amount
        amount = calculate_risk_amount(100000, 1.0)
        assert amount == 1000


class TestATRBased:
    """Tests for ATR-based risk model."""

    def test_atr_stop_long(self):
        """ATR stop for long should be entry - (atr * multiplier)."""
        from research_modules.risk_models.models.atr_based import calculate_atr_stop
        # Entry = 100, ATR = 2, Mult = 2 → Stop = 100 - 4 = 96
        stop = calculate_atr_stop(100, 2, 2.0, "LONG")
        assert stop == 96

    def test_atr_stop_short(self):
        """ATR stop for short should be entry + (atr * multiplier)."""
        from research_modules.risk_models.models.atr_based import calculate_atr_stop
        stop = calculate_atr_stop(100, 2, 2.0, "SHORT")
        assert stop == 104

    def test_position_from_atr(self):
        """Position size from ATR should account for ATR-based stop."""
        from research_modules.risk_models.models.atr_based import calculate_position_from_atr
        # Capital = 100000, Risk = 1%, Entry = 100, ATR = 2, Mult = 2
        # Stop Distance = 4, Risk Amount = 1000
        # Position = 1000 / 4 = 250
        size = calculate_position_from_atr(100000, 1.0, 100, 2, 2.0)
        assert size == 250


class TestPercentEquity:
    """Tests for percent of equity model."""

    def test_max_position_value(self):
        """Max position value should be equity * pct / 100."""
        from research_modules.risk_models.models.percent_equity import calculate_max_position_value
        value = calculate_max_position_value(100000, 10.0)
        assert value == 10000

    def test_max_shares(self):
        """Max shares should be max_value / price."""
        from research_modules.risk_models.models.percent_equity import calculate_max_shares
        # Equity = 100000, Price = 50, Max Pct = 10%
        # Max Value = 10000, Shares = 200
        shares = calculate_max_shares(100000, 50, 10.0)
        assert shares == 200


class TestMaxLossGuard:
    """Tests for max loss guard model."""

    def test_daily_loss_limit_allowed(self):
        """Should allow trade if within daily limit."""
        from research_modules.risk_models.models.max_loss_guard import check_daily_loss_limit
        result = check_daily_loss_limit(500, 200, 1000)
        assert result.allowed is True

    def test_daily_loss_limit_exceeded(self):
        """Should reject trade if exceeds daily limit."""
        from research_modules.risk_models.models.max_loss_guard import check_daily_loss_limit
        result = check_daily_loss_limit(800, 300, 1000)
        assert result.allowed is False

    def test_trade_loss_limit_allowed(self):
        """Should allow trade if within per-trade limit."""
        from research_modules.risk_models.models.max_loss_guard import check_trade_loss_limit
        result = check_trade_loss_limit(500, 1000)
        assert result.allowed is True

    def test_trade_loss_limit_exceeded(self):
        """Should reject trade if exceeds per-trade limit."""
        from research_modules.risk_models.models.max_loss_guard import check_trade_loss_limit
        result = check_trade_loss_limit(1500, 1000)
        assert result.allowed is False


class TestRiskMetrics:
    """Tests for risk metrics calculations."""

    def test_r_multiple_win(self):
        """R-multiple for winning trade should be positive."""
        from research_modules.risk_models.risk_metrics import calculate_r_multiple
        r = calculate_r_multiple(pnl=2000, initial_risk=1000)
        assert r == 2.0

    def test_r_multiple_loss(self):
        """R-multiple for losing trade should be negative."""
        from research_modules.risk_models.risk_metrics import calculate_r_multiple
        r = calculate_r_multiple(pnl=-500, initial_risk=1000)
        assert r == -0.5

    def test_worst_case_loss(self):
        """Worst case loss should be position * stop distance."""
        from research_modules.risk_models.risk_metrics import calculate_worst_case_loss
        loss = calculate_worst_case_loss(100, 100, 95)
        assert loss == 500

    def test_kelly_fraction(self):
        """Kelly fraction should be positive for edge-positive system."""
        from research_modules.risk_models.risk_metrics import calculate_kelly_fraction
        # Win rate = 60%, Win/Loss ratio = 2
        # Kelly = 0.6 - (0.4 / 2) = 0.6 - 0.2 = 0.4
        kelly = calculate_kelly_fraction(0.6, 2.0)
        assert kelly == pytest.approx(0.4)
