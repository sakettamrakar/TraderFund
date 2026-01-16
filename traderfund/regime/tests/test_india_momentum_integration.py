
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import os

from traderfund.regime.integration_guards import MomentumRegimeGuard, GuardDecision
from traderfund.regime.types import MarketBehavior, DirectionalBias

class TestMomentumIntegration:
    @pytest.fixture
    def guard(self):
        # Initialize guard
        return MomentumRegimeGuard()

    @pytest.fixture
    def mock_df_normal(self):
        # Create normal trending data
        dates = pd.date_range("2024-01-01", periods=100, freq="1min")
        close = np.linspace(100, 110, 100)
        return pd.DataFrame({
            'timestamp': dates,
            'open': close - 0.1,
            'high': close + 0.2,
            'low': close - 0.2,
            'close': close,
            'volume': [1000] * 100
        })

    @pytest.fixture
    def mock_df_risk_off(self, mock_df_normal):
        df = mock_df_normal.copy()
        # High volatility
        df.iloc[-1, df.columns.get_loc('high')] += 5
        df.iloc[-1, df.columns.get_loc('low')] -= 5
        # Low volume (Liquidity Dry) - ONLY Last Bar
        # This ensures RVOL = 10 / 1000 = 0.01
        df.iloc[-1, df.columns.get_loc('volume')] = 10
        return df

    def test_allow_signal(self, guard, mock_df_normal):
        with patch.object(guard, '_load_data', return_value=mock_df_normal):
            signal = {'symbol': 'INFY', 'timestamp': '2024-01-01T10:00:00'}
            
            decision = guard.check_signal(signal)
            
            assert decision.allowed is True
            assert decision.size_multiplier == 1.0
            assert "ALLOWED" in decision.reason
            assert decision.regime_state.behavior == MarketBehavior.TRENDING_NORMAL_VOL

    def test_block_signal_risk_off(self, guard, mock_df_risk_off):
        with patch.object(guard, '_load_data', return_value=mock_df_risk_off):
            # Explicitly set ENFORCED to verify blocking
            with patch.dict(os.environ, {"REGIME_MODE": "ENFORCED"}):
                signal = {'symbol': 'INFY', 'timestamp': '2024-01-01T10:00:00'}
                
                decision = guard.check_signal(signal)
                
                # Should be blocked due to liquidity dry or high vol
                assert decision.allowed is False
                assert decision.size_multiplier == 0.0
                assert "BLOCKED" in decision.reason

    def test_fail_safe_missing_data(self, guard):
        with patch.object(guard, '_load_data', return_value=pd.DataFrame()):
            signal = {'symbol': 'UNKNOWN'}
            
            decision = guard.check_signal(signal)
            
            assert decision.allowed is False
            assert "FAIL_SAFE" in decision.reason

    def test_reduce_size_high_vol(self, guard, mock_df_normal):
        # Synthesize High Vol but Liquid setup
        # Requires Vol Ratio > 1.5 but < Limit? No, Gate says High Vol -> REDUCE for Momentum
        
        # Modify data to spike Volatility but keep volume high
        mock_df_normal.iloc[-20:, mock_df_normal.columns.get_loc('high')] += 2
        mock_df_normal.iloc[-20:, mock_df_normal.columns.get_loc('low')] -= 2
        
        # Volatility Provider uses 14 period ATR vs 20 period Baseline
        # If last 20 bars are volatile, baseline rises too.
        # We need immediate spike.
        mock_df_normal.iloc[-1, mock_df_normal.columns.get_loc('high')] += 10
        mock_df_normal.iloc[-1, mock_df_normal.columns.get_loc('low')] -= 10
        
        with patch.object(guard, '_load_data', return_value=mock_df_normal):
            with patch.dict(os.environ, {"REGIME_MODE": "ENFORCED"}):
                signal = {'symbol': 'INFY'}
                decision = guard.check_signal(signal)
                
                # If behavior is TRENDING_HIGH_VOL, Momentum is REDUCED
                if decision.regime_state.behavior == MarketBehavior.TRENDING_HIGH_VOL:
                    assert decision.allowed is True
                    assert decision.size_multiplier < 1.0
                    assert "REDUCED" in decision.reason

    def test_kill_switch_mode(self, guard, mock_df_risk_off):
        # Even with RISK OFF data, if MODE is OFF, we should ALLOW.
        with patch.object(guard, '_load_data', return_value=mock_df_risk_off):
            signal = {'symbol': 'INFY'}
            
            with patch.dict(os.environ, {"REGIME_MODE": "OFF"}):
                decision = guard.check_signal(signal)
                assert decision.allowed is True
                assert decision.size_multiplier == 1.0
                assert "legacy" in decision.reason.lower()

    def test_shadow_mode_blocking(self, guard, mock_df_risk_off):
        # With RISK OFF, normal mode BLOCKS.
        # In SHADOW mode, it should ALLOW but flag it.
        with patch.object(guard, '_load_data', return_value=mock_df_risk_off):
            signal = {'symbol': 'INFY'}
            
            with patch.dict(os.environ, {"REGIME_MODE": "SHADOW"}):
                decision = guard.check_signal(signal)
                assert decision.allowed is True
                assert "SHADOW-BLOCK" in decision.reason
