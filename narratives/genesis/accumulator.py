"""
Accumulation Buffer for Weak Signal Promotion.

This module implements the logic to capture LOW severity events
and promote them to SYNTHETIC_MEDIUM when a theme accumulates.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from narratives.core.models import Event
from narratives.core.enums import EventType
from signals.core.enums import Market

logger = logging.getLogger("AccumulationBuffer")

# =============================================================================
# CONSTANTS (FROZEN)
# =============================================================================

ACCUMULATION_THRESHOLD = 3          # Number of LOW events to trigger promotion
ACCUMULATION_WINDOW_HOURS = 48      # Rolling window in hours
SYNTHETIC_SEVERITY = 65.0           # Severity score for promoted events
DEFAULT_TAG = "_UNTAGGED_"          # Fallback for events without semantic tags


@dataclass
class BufferedEvent:
    """Wrapper for events in the buffer with timestamp tracking."""
    event: Event
    timestamp: datetime
    semantic_tag: str


class AccumulationBuffer:
    """
    In-memory buffer for LOW severity events.
    
    Groups events by semantic_tag and promotes to SYNTHETIC_MEDIUM
    when ACCUMULATION_THRESHOLD events are seen within the rolling window.
    """
    
    def __init__(self, window_hours: int = ACCUMULATION_WINDOW_HOURS):
        self.window = timedelta(hours=window_hours)
        self._buffer: Dict[str, List[BufferedEvent]] = defaultdict(list)
        
        # Metrics
        self.metrics = {
            "low_events_buffered": 0,
            "synthetic_events_promoted": 0,
            "tags_active": 0
        }
    
    def add_event(self, event: Event) -> Optional[Event]:
        """
        Add a LOW event to the buffer.
        Returns a SYNTHETIC_MEDIUM event if promotion threshold is met, else None.
        """
        now = datetime.utcnow()
        
        # Extract semantic tag from payload
        tags = event.payload.get("semantic_tags", [])
        tag = tags[0] if tags else DEFAULT_TAG
        
        # Wrap and store
        buffered = BufferedEvent(event=event, timestamp=now, semantic_tag=tag)
        self._buffer[tag].append(buffered)
        self.metrics["low_events_buffered"] += 1
        
        # Prune expired events for this tag
        self._prune_tag(tag, now)
        
        # Check for promotion
        if len(self._buffer[tag]) >= ACCUMULATION_THRESHOLD:
            return self._promote(tag, now)
        
        return None
    
    def _prune_tag(self, tag: str, now: datetime):
        """Remove events older than the rolling window."""
        cutoff = now - self.window
        self._buffer[tag] = [
            b for b in self._buffer[tag] if b.timestamp > cutoff
        ]
    
    def _promote(self, tag: str, now: datetime) -> Event:
        """
        Create a SYNTHETIC_MEDIUM event from accumulated LOW events.
        Clears the buffer for this tag after promotion.
        """
        events_in_tag = self._buffer[tag]
        event_ids = [b.event.event_id for b in events_in_tag]
        
        # Build synthetic payload
        payload = {
            "signal_name": f"ACCUMULATED: {tag} ({len(events_in_tag)} events)",
            "accumulated": True,
            "source_event_ids": event_ids,
            "semantic_tags": [tag],
            "shadow": True  # Inherited from source events
        }
        
        # Create synthetic event
        # Use the market from the first event (assumption: same market)
        base_event = events_in_tag[0].event
        
        synthetic = Event.create(
            etype=EventType.MACRO,
            market=base_event.market,
            time=now,
            severity=SYNTHETIC_SEVERITY,
            source="ACCUMULATION_BUFFER",
            payload=payload,
            asset=base_event.asset_id or "GLOBAL_MARKET"
        )
        
        logger.info(f"ACCUMULATION_PROMOTED: {tag} ({len(events_in_tag)} events) -> Synthetic Event {synthetic.event_id}")
        
        # Clear buffer for this tag
        self._buffer[tag] = []
        self.metrics["synthetic_events_promoted"] += 1
        
        return synthetic
    
    def get_active_tags(self) -> List[str]:
        """Return list of tags with buffered events."""
        return [tag for tag, events in self._buffer.items() if events]
    
    def reset_metrics(self):
        """Reset metrics for a new run."""
        self.metrics = {k: 0 for k in self.metrics}
        self.metrics["tags_active"] = len(self.get_active_tags())
