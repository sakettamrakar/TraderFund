import logging
from typing import List, Dict, Optional
from narratives.core.models import Narrative, Event
from narratives.core.enums import NarrativeState, NarrativeScope, EventType
from narratives.repository.base import NarrativeRepository
from signals.core.enums import Market

logger = logging.getLogger("NarrativeEngine")

class NarrativeGenesisEngine:
    """
    Deterministically converts specific events into Narratives.
    """
    
    MIN_SEVERITY_FOR_GENESIS = 60.0
    
    def __init__(self, repo: NarrativeRepository):
        self.repo = repo

    def ingest_events(self, market: Market, events: List[Event]):
        active_narratives = self.repo.get_active_narratives(market)
        logger.info(f"Ingesting {len(events)} events for {market.value}. Active Narratives: {len(active_narratives)}")
        
        # Index Active Narratives by Asset for O(1) matching (Simplistic clustering)
        # One asset can belong to multiple narratives, so Dict[asset, List[Narrative]]
        narrative_map: Dict[str, List[Narrative]] = {}
        for n in active_narratives:
             if n.scope == NarrativeScope.ASSET:
                 for asset in n.related_assets:
                     narrative_map.setdefault(asset, []).append(n)

        for event in events:
             self._process_single_event(event, narrative_map)

    def _process_single_event(self, event: Event, narrative_map: Dict[str, List[Narrative]]):
        # 1. Clustering Logic
        # Try to find existing narrative matching Asset
        matched = False
        if event.asset_id and event.asset_id in narrative_map:
             existing_list = narrative_map[event.asset_id]
             # Simple Logic: Attach to the first valid one.
             # Real logic would check context/direction compatibility.
             target_narrative = existing_list[0]
             
             self._reinforce_narrative(target_narrative, event)
             matched = True
        
        # 2. Genesis Logic
        if not matched:
            if event.severity_score >= self.MIN_SEVERITY_FOR_GENESIS:
                 self._create_narrative(event)
            else:
                 # Event is noise (orphan)
                 pass

    def _create_narrative(self, event: Event):
        # Title Generation (Template based)
        title = f"New {event.event_type.value} on {event.asset_id}"
        if event.payload.get('signal_name'):
             title = f"{event.payload['signal_name']} detected on {event.asset_id}"
             
        explanation = {
             "genesis_event": event.event_id,
             "genesis_type": event.event_type.value
        }
        
        narrative = Narrative.create(
             title=title,
             market=event.market,
             scope=NarrativeScope.ASSET if event.asset_id else NarrativeScope.MARKET,
             assets=[event.asset_id] if event.asset_id else [],
             events=[event.event_id],
             confidence=event.severity_score * 0.8, # Initial confidence discount
             explanation=explanation
        )
        self.repo.save_narrative(narrative)
        logger.info(f"GENESIS: Created Narrative {narrative.narrative_id} from {event.event_id}")

    def _reinforce_narrative(self, narrative: Narrative, event: Event):
        # Calculate new confidence
        # Simple Weighted Average Model
        # New Conf = (Old * 0.9) + (EventSev * 0.1) + ReinforcementBonus
        new_conf = min(0.99, narrative.confidence_score + (event.severity_score * 0.1))
        
        updated = narrative.add_events(
             new_events=[event.event_id],
             new_confidence=new_conf
        )
        self.repo.save_narrative(updated)
        logger.info(f"REINFORCED: Narrative {updated.narrative_id} with {event.event_id}")
