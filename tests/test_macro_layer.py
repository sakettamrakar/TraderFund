import pytest
from datetime import datetime
from unittest.mock import patch
from src.layers.macro_layer import MacroLayer, MacroSnapshot, RegimeState, RateEnvironment, HealthStatus, ComponentHealth

class TestMacroLayer:
    def test_initialization(self):
        """Test initial state of MacroLayer."""
        layer = MacroLayer()
        assert layer.get_current() is None
        assert layer.get_regime() == RegimeState.UNDEFINED
        assert layer.get_rate_environment() == RateEnvironment.UNDEFINED
        
        health = layer.get_health()
        assert isinstance(health, ComponentHealth)
        assert health.health_status == HealthStatus.OK
        assert health.failure_count == 0
        assert health.last_success_timestamp is None
        assert health.degraded_reason is None

    def test_get_health(self):
        """Test get_health returns the current health component."""
        layer = MacroLayer()
        initial_health = layer.get_health()
        assert initial_health.health_status == HealthStatus.OK
        assert layer.get_health() == initial_health

    def test_update_snapshot_success(self):
        """Test successful update of the macro snapshot and health status."""
        layer = MacroLayer()
        
        time_before_update = datetime.now()
        
        snapshot = MacroSnapshot(
            regime=RegimeState.EXPANSION,
            regime_confidence=0.8,
            rate_environment=RateEnvironment.RISING,
            inflation_trend="ACCELERATING"
        )
        layer.update_snapshot(snapshot)
        
        current = layer.get_current()
        assert current is not None
        assert current == snapshot
        assert layer.get_regime() == RegimeState.EXPANSION
        assert layer.get_rate_environment() == RateEnvironment.RISING
        
        health = layer.get_health()
        assert health.health_status == HealthStatus.OK
        assert health.failure_count == 0
        assert health.last_success_timestamp is not None
        assert health.last_success_timestamp >= time_before_update
        assert health.degraded_reason is None

    def test_update_snapshot_failure(self):
        """Test that a failed update correctly sets health status to FAILED."""
        layer = MacroLayer()
        initial_health = layer.get_health()

        # Mock datetime.now() to raise an exception to test the except block
        with patch('src.layers.macro_layer.datetime') as mock_datetime:
            mock_datetime.now.side_effect = ValueError("Time machine is broken")
            layer.update_snapshot(MacroSnapshot())
        
        health = layer.get_health()
        assert health.health_status == HealthStatus.FAILED
        assert health.failure_count == 1
        assert "Time machine is broken" in health.degraded_reason
        
        # Last success timestamp should not have been updated
        assert health.last_success_timestamp == initial_health.last_success_timestamp
        
        # A second failure should increment the count
        with patch('src.layers.macro_layer.datetime') as mock_datetime:
            mock_datetime.now.side_effect = ValueError("Time machine is broken again")
            layer.update_snapshot(MacroSnapshot())
        
        health = layer.get_health()
        assert health.health_status == HealthStatus.FAILED
        assert health.failure_count == 2

    def test_history_is_maintained(self):
        """Test that history of snapshots is maintained."""
        layer = MacroLayer()
        snap1 = MacroSnapshot(regime=RegimeState.EXPANSION)
        snap2 = MacroSnapshot(regime=RegimeState.CONTRACTION)
        
        layer.update_snapshot(snap1)
        layer.update_snapshot(snap2)
        
        assert layer.get_current() == snap2
        assert len(layer._history) == 1
        assert layer._history[0] == snap1

    def test_recovery_after_failure(self):
        """Test that the component can recover after a failure."""
        layer = MacroLayer()

        # Fail first
        with patch('src.layers.macro_layer.datetime') as mock_datetime:
            mock_datetime.now.side_effect = ValueError("Time machine is broken")
            layer.update_snapshot(MacroSnapshot())
        
        failed_health = layer.get_health()
        assert failed_health.health_status == HealthStatus.FAILED
        assert failed_health.failure_count == 1

        # Then succeed
        snapshot = MacroSnapshot(regime=RegimeState.RECOVERY)
        layer.update_snapshot(snapshot)

        recovered_health = layer.get_health()
        assert recovered_health.health_status == HealthStatus.OK
        assert recovered_health.failure_count == 1 
