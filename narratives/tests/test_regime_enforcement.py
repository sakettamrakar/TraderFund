# Test: Runtime Narrative Enforcement
#
# These tests verify that ALL narratives pass through regime enforcement.

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

from narratives.core.models import Narrative, Event
from narratives.core.enums import NarrativeState, NarrativeScope, EventType
from narratives.repository.base import NarrativeRepository
from narratives.repository.regime_enforced import (
    RegimeEnforcedRepository,
    wrap_with_regime_enforcement,
    _get_regime_snapshot
)
from signals.core.enums import Market


class MockRepository(NarrativeRepository):
    """Mock repository for testing."""
    
    def __init__(self):
        self.saved_narratives = []
    
    def save_narrative(self, narrative: Narrative) -> None:
        self.saved_narratives.append(narrative)
    
    def get_narrative_history(self, narrative_id: str):
        return []
    
    def get_active_narratives(self, market: Market):
        return []


class TestRegimeEnforcedRepository:
    
    def test_all_narratives_pass_through_wrapper(self):
        """Every narrative saved MUST pass through regime enforcement."""
        mock_repo = MockRepository()
        enforced_repo = RegimeEnforcedRepository(mock_repo)
        
        narrative = Narrative.create(
            title="Test Narrative",
            market=Market.US,
            scope=NarrativeScope.ASSET,
            assets=["AAPL"],
            events=["event-1"],
            confidence=0.8,
            explanation={"test": True}
        )
        
        enforced_repo.save_narrative(narrative)
        
        # Verify narrative was saved
        assert len(mock_repo.saved_narratives) == 1
        
        # Verify regime metadata was attached
        saved = mock_repo.saved_narratives[0]
        assert "regime_enforcement" in saved.explainability_payload
    
    def test_regime_metadata_attached(self):
        """Verify all regime fields are attached to narrative."""
        mock_repo = MockRepository()
        enforced_repo = RegimeEnforcedRepository(mock_repo)
        
        narrative = Narrative.create(
            title="Test",
            market=Market.US,
            scope=NarrativeScope.ASSET,
            assets=["MSFT"],
            events=["event-2"],
            confidence=1.0,
            explanation={}
        )
        
        enforced_repo.save_narrative(narrative)
        saved = mock_repo.saved_narratives[0]
        
        metadata = saved.explainability_payload["regime_enforcement"]
        
        # All required fields must be present
        assert "regime" in metadata
        assert "bias" in metadata
        assert "regime_confidence" in metadata
        assert "lifecycle" in metadata
        assert "original_weight" in metadata
        assert "final_weight" in metadata
        assert "multiplier" in metadata
        assert "enforcement_reason" in metadata
        assert "enforced_at" in metadata
    
    def test_event_lock_mutes_narrative(self):
        """EVENT_LOCK must result in final_weight == 0.0."""
        mock_repo = MockRepository()
        enforced_repo = RegimeEnforcedRepository(mock_repo)
        
        # Mock EVENT_LOCK regime
        with patch('narratives.repository.regime_enforced._get_regime_snapshot') as mock_regime:
            mock_regime.return_value = {
                "regime": "EVENT_LOCK",
                "bias": "NEUTRAL",
                "confidence": 1.0,
                "lifecycle": "STABLE",
                "narrative_weight": 0.0,
                "enforcement_reason": "NARRATIVE_MUTED: EVENT_LOCK (0.0x)"
            }
            
            narrative = Narrative.create(
                title="Test",
                market=Market.US,
                scope=NarrativeScope.ASSET,
                assets=["TSLA"],
                events=["event-3"],
                confidence=1.0,
                explanation={}
            )
            
            enforced_repo.save_narrative(narrative)
        
        saved = mock_repo.saved_narratives[0]
        assert saved.confidence_score == 0.0
    
    def test_missing_regime_fails_safe(self):
        """Missing regime must dampen to 0.5x."""
        mock_repo = MockRepository()
        enforced_repo = RegimeEnforcedRepository(mock_repo)
        
        # Mock missing regime
        with patch('narratives.repository.regime_enforced._get_regime_snapshot') as mock_regime:
            mock_regime.return_value = {
                "regime": "UNDEFINED",
                "bias": "NEUTRAL",
                "confidence": 0.0,
                "lifecycle": "UNKNOWN",
                "narrative_weight": 0.5,
                "enforcement_reason": "FAIL_SAFE_DAMPEN"
            }
            
            narrative = Narrative.create(
                title="Test",
                market=Market.US,
                scope=NarrativeScope.ASSET,
                assets=["NVDA"],
                events=["event-4"],
                confidence=1.0,
                explanation={}
            )
            
            enforced_repo.save_narrative(narrative)
        
        saved = mock_repo.saved_narratives[0]
        assert saved.confidence_score == 0.5


class TestNoBypassPath:
    
    def test_wrapper_factory_returns_enforced_repo(self):
        """wrap_with_regime_enforcement must return RegimeEnforcedRepository."""
        mock_repo = MockRepository()
        wrapped = wrap_with_regime_enforcement(mock_repo)
        
        assert isinstance(wrapped, RegimeEnforcedRepository)
    
    def test_wrapper_cannot_be_unwrapped(self):
        """There is no public method to unwrap the repository."""
        mock_repo = MockRepository()
        wrapped = wrap_with_regime_enforcement(mock_repo)
        
        # No public unwrap method
        assert not hasattr(wrapped, 'unwrap')
        assert not hasattr(wrapped, 'get_inner')
        
        # Inner repo is private
        assert hasattr(wrapped, '_inner')


class TestRegimeSnapshot:
    
    def test_snapshot_returns_valid_structure(self):
        """_get_regime_snapshot must return all required fields."""
        snapshot = _get_regime_snapshot()
        
        assert "regime" in snapshot
        assert "bias" in snapshot
        assert "confidence" in snapshot
        assert "lifecycle" in snapshot
        assert "narrative_weight" in snapshot
        assert "enforcement_reason" in snapshot
