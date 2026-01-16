
import pytest
import os
import json
from unittest.mock import patch, call
from traderfund.regime.dashboard import RegimeDashboard

class TestRegimeDashboard:
    TEST_LOG = "test_dashboard_shadow.jsonl"
    
    @classmethod
    def setup_class(cls):
        # Create a sample log file
        data = {
            "meta": {"symbol": "INFY", "timestamp": "2024-01-01T12:00:00"},
            "regime": {
                "behavior": "TRENDING_NORMAL_VOL",
                "bias": "BULLISH",
                "is_stable": True,
                "total_confidence": 0.85,
                "confidence_detail": {"confluence": 0.8, "persistence": 0.9, "intensity": 0.8}
            },
            "factors": {"trend": 0.7, "vol_ratio": 1.0, "event": 0.0, "liquidity": "NORMAL"},
            "constraints": {"blocked_strategies": [], "throttled_strategies": []},
            "shadow": {"would_block": [], "cooldown_active": False}
        }
        with open(cls.TEST_LOG, 'w') as f:
            f.write(json.dumps(data) + "\n")

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.TEST_LOG):
            os.remove(cls.TEST_LOG)

    def test_read_state(self):
        dash = RegimeDashboard(log_file=self.TEST_LOG)
        state = dash._read_latest_state()
        
        assert state is not None
        assert state['meta']['symbol'] == "INFY"
        assert state['regime']['behavior'] == "TRENDING_NORMAL_VOL"

    def test_draw_ui(self):
        # Smoke test for rendering logic (no crash)
        dash = RegimeDashboard(log_file=self.TEST_LOG)
        state = dash._read_latest_state()
        
        with patch('builtins.print') as mock_print:
            dash._draw_ui(state)
            
            # Verify key information is printed
            # Behavior
            assert any("TRENDING_NORMAL_VOL" in str(c) for c in mock_print.call_args_list)
            # Confidence
            assert any("0.85" in str(c) for c in mock_print.call_args_list)
            # Metrics
            assert any("NORMAL" in str(c) for c in mock_print.call_args_list)

    def test_draw_ui_no_data(self):
        dash = RegimeDashboard(log_file="nonexistent.log")
        with patch('builtins.print') as mock_print:
            dash._draw_ui(None)
            assert any("Waiting for data" in str(c) for c in mock_print.call_args_list)
