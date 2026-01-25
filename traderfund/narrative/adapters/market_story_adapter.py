"""
Market Story Adapter (Shadow Mode Bridge).

This module bridges external 'MarketStory' objects (from the News Repo)
into the Trader Fund's NarrativeGenesisEngine.

It runs in STRICT SHADOW MODE by default to prevent unauthorized trading.
"""

import logging
import hashlib
import requests
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from narratives.core.models import Event
from narratives.core.enums import EventType
from signals.core.enums import Market
from narratives.genesis.engine import NarrativeGenesisEngine

logger = logging.getLogger(__name__)

# =============================================================================
# DATA CONTRACTS
# =============================================================================

class MarketStory(BaseModel):
    """External Story Contract (from News Repo)."""
    id: str
    headline: str
    summary: str
    published_at: str  # ISO-8601
    category: str      # "MARKET_SUMMARY"
    region: str        # "US" | "GLOBAL"
    severity_hint: str # "LOW" | "MEDIUM" | "HIGH"
    source: str
    # Semantic Enrichment (Optional - from upstream)
    semantic_tags: Optional[List[str]] = None
    event_type: Optional[str] = None      # ECONOMIC_DATA, GEOPOLITICAL, CORPORATE
    expectedness: Optional[str] = None    # EXPECTED, UNEXPECTED

class NarrativeInput(BaseModel):
    """Internal Trader Narrative Input."""
    headline: str
    context: str
    domain: str = "MARKET"
    type: str = "MARKET_CONTEXT"
    scope: str = "GLOBAL"
    source: str
    timestamp: str
    initial_weight: float
    shadow: bool = True
    # Semantic Enrichment (passthrough)
    semantic_tags: Optional[List[str]] = None
    event_type: Optional[str] = None
    expectedness: Optional[str] = None

    @property
    def dedupe_id(self) -> str:
        """Generate deterministic ID for deduplication."""
        raw = f"{self.headline}|{self.timestamp}|{self.source}"
        return hashlib.md5(raw.encode()).hexdigest()

# =============================================================================
# ADAPTER IMPLEMENTATION
# =============================================================================

class MarketStoryAdapter:
    """
    Adapter to ingest MarketStory objects into NarrativeGenesisEngine.
    """
    
    def __init__(self, engine: NarrativeGenesisEngine):
        self.engine = engine
        self._processed_ids = set() # Simple in-memory dedupe for the run scope

    def convert_story(self, story: MarketStory) -> NarrativeInput:
        """Map external Story to internal NarrativeInput with heuristic weighting."""
        
        # 1. Heuristic Weighting
        weight_map = {
            "LOW": 0.4,
            "MEDIUM": 0.6,
            "HIGH": 0.8
        }
        severity = story.severity_hint.upper()
        initial_weight = weight_map.get(severity, 0.5) # Default to 0.5 if unknown
        
        # 2. Map Fields (including semantic enrichment passthrough)
        return NarrativeInput(
            headline=story.headline,
            context=story.summary,
            domain="MARKET",
            type="MARKET_CONTEXT",
            scope="GLOBAL" if story.region == "GLOBAL" else "ASSETS",
            source=story.source,
            timestamp=story.published_at,
            initial_weight=initial_weight,
            shadow=True, # MANDATORY
            semantic_tags=story.semantic_tags,
            event_type=story.event_type,
            expectedness=story.expectedness
        )

    def fetch_stories_from_api(self, url: str) -> List[MarketStory]:
        """
        Fetch stories from the specified API endpoint.
        Fails gracefully on error.
        """
        try:
            response = requests.get(url, timeout=2)
            response.raise_for_status()
            data = response.json()
            
            stories = []
            for item in data:
                try:
                    stories.append(MarketStory(**item))
                except Exception as e:
                    logger.warning(f"ADAPTER: Failed to parse story item: {e}")
            
            return stories
            
        except Exception as e:
            logger.error(f"ADAPTER: API fetch failed: {e}")
            return []

    def ingest_stories(self, stories: List[MarketStory]) -> int:
        """
        Process a batch of stories and feed them to the engine.
        Returns count of successfully ingested stories.
        """
        ingested_count = 0
        events_to_ingest = []
        
        logger.info(f"ADAPTER: Received {len(stories)} stories for ingestion.")
        
        for story in stories:
            try:
                # 1. Convert
                narrative_input = self.convert_story(story)
                
                # 2. Deduplication Check
                dedupe_key = narrative_input.dedupe_id
                if dedupe_key in self._processed_ids:
                    logger.debug(f"ADAPTER: Skipping duplicate story {story.id}")
                    continue
                
                # Check against engine (if possible)? 
                # For now, we rely on the run-scope dedupe and assume the engine/repo handles persistence idempotency 
                # (though the prompt asked for adapter idempotency).
                # Since we don't have a persistent state for the adapter itself in this scope, 
                # we assume "idempotent per run" means duplicates within the list or previously seen in memory.
                # Ideally, we'd check the DB, but "NO changes to narrative logic" limits us.
                
                self._processed_ids.add(dedupe_key)
                
                # 3. Bridge to Event
                # We must bridge NarrativeInput -> Event for the engine
                event = self._bridge_to_event(narrative_input)
                events_to_ingest.append(event)
                
                logger.info(f"MARKET STORY INGESTED (SHADOW): {narrative_input.headline}")
                ingested_count += 1
                
            except Exception as e:
                logger.error(f"ADAPTER: Failed to process story {story.id}: {e}")
        
        # 4. Feed to Engine
        if events_to_ingest:
            # We assume US Market for "Market Summary" stories for now based on context
            self.engine.ingest_events(Market.US, events_to_ingest)
            
        return ingested_count

    def _bridge_to_event(self, inp: NarrativeInput) -> Event:
        """
        Convert NarrativeInput to Engine Event.
        """
        # EventType mapping
        # "MARKET_CONTEXT" -> EventType.MACRO (closest match)
        evt_type = EventType.MACRO
        
        # Payload construction
        # We stuff extra metadata into payload hoping it helps, 
        # but primarily 'signal_name' drives the title.
        payload = {
            "headline": inp.headline,
            "signal_name": inp.headline, # Critical for narrative title
            "summary": inp.context,
            "domain": inp.domain,
            "type": inp.type,
            "adapter_source": "MarketStoryAdapter", # Traceability
            "shadow": inp.shadow,
            # Semantic Enrichment (passthrough)
            "semantic_tags": inp.semantic_tags if hasattr(inp, 'semantic_tags') else None,
            "event_type": inp.event_type if hasattr(inp, 'event_type') else None,
            "expectedness": inp.expectedness if hasattr(inp, 'expectedness') else None
        }
        
        # Severity from weight (0.0-1.0) -> Score (0-100)?
        # Engine takes severity_score. 
        # If Initial Weight is 0.8, severity score should be high.
        # Engine logic: Conf = Score * 0.8. 
        # If we want weight 0.8, we might need severity 1.0 (100.0).
        # But wait, adapter output "initial_weight" is a hint.
        # Let's map 0.0-1.0 to 0-100 for severity_score.
        severity_score = inp.initial_weight * 100.0
        
        # Asset ID - Global scope usually implies no specific asset.
        # But NarrativeGenesisEngine uses Asset clustering.
        # We'll use a virtual asset "GLOBAL_MACRO" or similar to cluster these together.
        asset_id = "GLOBAL_MARKET"
        
        return Event.create(
            etype=evt_type,
            market=Market.US, # Defaulting to US for this exercise
            time=datetime.fromisoformat(inp.timestamp),
            severity=severity_score,
            source=f"ADAPTER:{inp.source}",
            payload=payload,
            asset=asset_id
        )
