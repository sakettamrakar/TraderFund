"""
Tests for Market Story Adapter.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from traderfund.narrative.adapters.market_story_adapter import MarketStoryAdapter, MarketStory, NarrativeInput
from narratives.genesis.engine import NarrativeGenesisEngine
from narratives.core.models import Event
from narratives.core.enums import EventType
from signals.core.enums import Market

@pytest.fixture
def mock_engine():
    return MagicMock(spec=NarrativeGenesisEngine)

@pytest.fixture
def adapter(mock_engine):
    return MarketStoryAdapter(mock_engine)

@pytest.fixture
def sample_story():
    return MarketStory(
        id="story-123",
        headline="Market hits all-time high",
        summary="A great day for stocks.",
        published_at=datetime.utcnow().isoformat(),
        category="MARKET_SUMMARY",
        region="GLOBAL",
        severity_hint="HIGH",
        source="Bloomberg"
    )

def test_convert_story_mapping(adapter, sample_story):
    """Test correct mapping from external story to internal input."""
    result = adapter.convert_story(sample_story)
    
    assert result.headline == sample_story.headline
    assert result.context == sample_story.summary
    assert result.domain == "MARKET"
    assert result.type == "MARKET_CONTEXT"
    assert result.scope == "GLOBAL"
    assert result.source == sample_story.source
    assert result.timestamp == sample_story.published_at
    assert result.shadow is True

def test_heuristic_weighting(adapter, sample_story):
    """Test severity hint to weight mapping."""
    # HIGH -> 0.8
    sample_story.severity_hint = "HIGH"
    assert adapter.convert_story(sample_story).initial_weight == 0.8
    
    # MEDIUM -> 0.6
    sample_story.severity_hint = "MEDIUM"
    assert adapter.convert_story(sample_story).initial_weight == 0.6
    
    # LOW -> 0.4
    sample_story.severity_hint = "LOW"
    assert adapter.convert_story(sample_story).initial_weight == 0.4
    
    # UNKNOWN -> 0.5
    sample_story.severity_hint = "FOO"
    assert adapter.convert_story(sample_story).initial_weight == 0.5

def test_deduplication(adapter, sample_story):
    """Test that duplicate stories are ignored."""
    # First ingestion
    count = adapter.ingest_stories([sample_story])
    assert count == 1
    assert adapter.engine.ingest_events.call_count == 1
    
    # Second ingestion (same story)
    count = adapter.ingest_stories([sample_story])
    assert count == 0
    # Engine should NOT have been called again (call_count stays 1)
    # Wait, ingest_events is called if 'events_to_ingest' list is not empty.
    # If list is empty, call_count should not increase.
    assert adapter.engine.ingest_events.call_count == 1

def test_bridge_to_event(adapter, sample_story):
    """Test conversion to Event."""
    # Trigger private bridge method via ingest (easiest way or mock)
    # Let's test _bridge_to_event directly for clarity since it's a unit test of the class logic
    inp = adapter.convert_story(sample_story)
    evt = adapter._bridge_to_event(inp)
    
    assert isinstance(evt, Event)
    assert evt.event_type == EventType.MACRO
    assert evt.payload['signal_name'] == sample_story.headline
    assert evt.payload['shadow'] is True
    assert evt.severity_score == 80.0 # HIGH -> 0.8 -> 80.0
    assert evt.asset_id == "GLOBAL_MARKET"
