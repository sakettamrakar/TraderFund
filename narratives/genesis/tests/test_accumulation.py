"""
Tests for Accumulation Logic.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from narratives.genesis.accumulator import AccumulationBuffer, ACCUMULATION_THRESHOLD, SYNTHETIC_SEVERITY
from narratives.genesis.engine import NarrativeGenesisEngine, HIGH_SEVERITY_FLOOR
from narratives.core.models import Event
from narratives.core.enums import EventType
from signals.core.enums import Market


def make_low_event(tag: str, headline: str = "Test Headline") -> Event:
    """Helper to create a LOW severity event with a semantic tag."""
    return Event.create(
        etype=EventType.MACRO,
        market=Market.US,
        time=datetime.utcnow(),
        severity=40.0,  # LOW
        source="TEST",
        payload={
            "signal_name": headline,
            "semantic_tags": [tag],
            "shadow": True
        },
        asset="GLOBAL_MARKET"
    )

# =============================================================================
# ACCUMULATION BUFFER TESTS
# =============================================================================

class TestAccumulationBuffer:

    def test_single_low_event_does_not_promote(self):
        """A single LOW event should be buffered but not promoted."""
        buffer = AccumulationBuffer()
        event = make_low_event("SUPPLY_CHAIN")
        
        result = buffer.add_event(event)
        
        assert result is None
        assert buffer.metrics["low_events_buffered"] == 1
        assert buffer.metrics["synthetic_events_promoted"] == 0

    def test_two_low_events_do_not_promote(self):
        """Two LOW events with same tag should not trigger promotion."""
        buffer = AccumulationBuffer()
        
        buffer.add_event(make_low_event("RATES"))
        result = buffer.add_event(make_low_event("RATES"))
        
        assert result is None
        assert buffer.metrics["low_events_buffered"] == 2

    def test_three_low_events_trigger_promotion(self):
        """Three LOW events with same tag should trigger promotion."""
        buffer = AccumulationBuffer()
        
        buffer.add_event(make_low_event("RATES", "Rate news 1"))
        buffer.add_event(make_low_event("RATES", "Rate news 2"))
        synthetic = buffer.add_event(make_low_event("RATES", "Rate news 3"))
        
        assert synthetic is not None
        assert synthetic.severity_score == SYNTHETIC_SEVERITY
        assert synthetic.payload.get("accumulated") is True
        assert buffer.metrics["synthetic_events_promoted"] == 1

    def test_different_tags_do_not_accumulate(self):
        """Events with different tags should not accumulate together."""
        buffer = AccumulationBuffer()
        
        buffer.add_event(make_low_event("RATES"))
        buffer.add_event(make_low_event("SUPPLY_CHAIN"))
        result = buffer.add_event(make_low_event("GEOPOLITICAL"))
        
        assert result is None
        assert len(buffer.get_active_tags()) == 3

# =============================================================================
# ENGINE INTEGRATION TESTS
# =============================================================================

class TestGenesisWithAccumulation:

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.get_active_narratives.return_value = []
        return repo

    def test_low_event_rejected_but_buffered(self, mock_repo):
        """LOW events should be rejected from Genesis but buffered."""
        engine = NarrativeGenesisEngine(repo=mock_repo, enforce_regime=False)
        
        event = make_low_event("SUPPLY_CHAIN")
        engine.ingest_events(Market.US, [event])
        
        assert engine.metrics["rejected"] == 1
        assert engine.metrics["narratives_created"] == 0
        assert engine.metrics["low_events_buffered"] == 1

    def test_accumulation_triggers_genesis(self, mock_repo):
        """Three LOW events should trigger accumulation and then genesis."""
        engine = NarrativeGenesisEngine(repo=mock_repo, enforce_regime=False)
        
        events = [
            make_low_event("RATES", "Rate news 1"),
            make_low_event("RATES", "Rate news 2"),
            make_low_event("RATES", "Rate news 3")
        ]
        engine.ingest_events(Market.US, events)
        
        # 3 rejected, but 1 synthetic promoted -> 1 narrative created
        assert engine.metrics["rejected"] == 3
        assert engine.metrics["synthetic_events_promoted"] == 1
        assert engine.metrics["narratives_created"] == 1
        assert engine.metrics["narratives_via_accumulation"] == 1

    def test_daily_cap_respected(self, mock_repo):
        """MEDIUM events should respect daily cap. HIGH bypasses."""
        engine = NarrativeGenesisEngine(repo=mock_repo, enforce_regime=False)
        engine.MAX_NARRATIVES_PER_DAY = 2  # Low cap for test
        
        # Create 3 MEDIUM events
        events = []
        for i in range(3):
            e = Event.create(
                etype=EventType.MACRO, market=Market.US, time=datetime.utcnow(),
                severity=70.0, source="TEST", payload={"signal_name": f"Med {i}", "shadow": True},
                asset="GLOBAL"
            )
            events.append(e)
        
        engine.ingest_events(Market.US, events)
        
        assert engine.metrics["narratives_created"] == 2
        assert engine.metrics["capped"] == 1

    def test_high_bypasses_cap(self, mock_repo):
        """HIGH severity events should bypass the daily cap."""
        engine = NarrativeGenesisEngine(repo=mock_repo, enforce_regime=False)
        engine.MAX_NARRATIVES_PER_DAY = 1
        engine._narratives_today = 1  # Already at cap
        
        high_event = Event.create(
            etype=EventType.MACRO, market=Market.US, time=datetime.utcnow(),
            severity=90.0, source="TEST", payload={"signal_name": "High Alert", "shadow": True},
            asset="GLOBAL"
        )
        
        engine.ingest_events(Market.US, [high_event])
        
        assert engine.metrics["narratives_created"] == 1
        assert engine.metrics["capped"] == 0
