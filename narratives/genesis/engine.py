import logging
from datetime import datetime, date
from typing import List, Dict, Optional
from narratives.core.models import Narrative, Event
from narratives.core.enums import NarrativeState, NarrativeScope, EventType
from narratives.repository.base import NarrativeRepository
from narratives.repository.regime_enforced import wrap_with_regime_enforcement
from narratives.genesis.accumulator import AccumulationBuffer
from signals.core.enums import Market

logger = logging.getLogger("NarrativeEngine")

# Severity thresholds (FROZEN)
HIGH_SEVERITY_FLOOR = 85.0  # HIGH events bypass daily cap

class NarrativeGenesisEngine:
    """
    Deterministically converts specific events into Narratives.
    
    REGIME ENFORCEMENT:
    All narratives are automatically regime-adjusted via the repository wrapper.
    There is NO bypass path. This behavior is FROZEN.
    """
    
    MIN_SEVERITY_FOR_GENESIS = 60.0
    MAX_NARRATIVES_PER_DAY = 5
    
    def __init__(self, repo: NarrativeRepository, enforce_regime: bool = True):
        # Wrap repository with regime enforcement (MANDATORY)
        if enforce_regime:
            self.repo = wrap_with_regime_enforcement(repo)
        else:
            # Only for testing - logs warning
            logger.warning("REGIME_BYPASSED: Running without regime enforcement (TEST MODE ONLY)")
            self.repo = repo
            
        # Accumulation Buffer
        self.accumulator = AccumulationBuffer()
        
        # Daily Cap Tracking
        self._narratives_today = 0
        self._current_date = date.today()
            
        # Metrics Initialization
        self.metrics = {
            "seen": 0,
            "rejected": 0,
            "promoted": 0,
            "narratives_created": 0,
            "shadow": 0,
            "low_events_buffered": 0,
            "synthetic_events_promoted": 0,
            "narratives_via_accumulation": 0,
            "capped": 0
        }

    def ingest_events(self, market: Market, events: List[Event]):
        # Reset Metrics for this run
        self.metrics = {k: 0 for k in self.metrics}
        self.accumulator.reset_metrics()
        
        # Reset daily cap if new day
        today = date.today()
        if today != self._current_date:
            self._current_date = today
            self._narratives_today = 0
            logger.info(f"NEW_DAY: Resetting daily narrative cap.")
        
        active_narratives = self.repo.get_active_narratives(market)
        logger.info(f"Ingesting {len(events)} events for {market.value}. Active Narratives: {len(active_narratives)}. Narratives Today: {self._narratives_today}/{self.MAX_NARRATIVES_PER_DAY}")
        
        # Index Active Narratives by Asset for O(1) matching (Simplistic clustering)
        narrative_map: Dict[str, List[Narrative]] = {}
        for n in active_narratives:
             if n.scope == NarrativeScope.ASSET:
                 for asset in n.related_assets:
                     narrative_map.setdefault(asset, []).append(n)

        for event in events:
             self._process_single_event(event, narrative_map)
             
        # Sync accumulator metrics
        self.metrics["low_events_buffered"] = self.accumulator.metrics["low_events_buffered"]
        self.metrics["synthetic_events_promoted"] = self.accumulator.metrics["synthetic_events_promoted"]
             
        self._log_metrics()

    def _log_metrics(self):
        """Emit structured genesis metrics."""
        m = self.metrics
        logger.info("\n" + "="*30)
        logger.info(" GENESIS_METRICS:")
        logger.info(f" seen: {m['seen']}")
        logger.info(f" rejected: {m['rejected']}")
        logger.info(f" promoted: {m['promoted']}")
        logger.info(f" narratives_created: {m['narratives_created']}")
        logger.info(f" shadow: {m['shadow']}")
        logger.info(f" low_events_buffered: {m['low_events_buffered']}")
        logger.info(f" synthetic_promoted: {m['synthetic_events_promoted']}")
        logger.info(f" via_accumulation: {m['narratives_via_accumulation']}")
        logger.info(f" capped: {m['capped']}")
        logger.info("="*30 + "\n")

    def _process_single_event(self, event: Event, narrative_map: Dict[str, List[Narrative]]):
        self.metrics["seen"] += 1
        
        # 1. Clustering Logic - Try to reinforce existing narrative
        if event.asset_id and event.asset_id in narrative_map:
             existing_list = narrative_map[event.asset_id]
             target_narrative = existing_list[0]
             self._reinforce_narrative(target_narrative, event)
             return  # Matched, done
        
        # 2. Genesis Logic - Check severity
        if event.severity_score >= self.MIN_SEVERITY_FOR_GENESIS:
            # Check daily cap (HIGH bypasses)
            is_high = event.severity_score >= HIGH_SEVERITY_FLOOR
            
            if not is_high and self._narratives_today >= self.MAX_NARRATIVES_PER_DAY:
                logger.info(f"GENESIS_CAPPED: {event.event_id} (daily cap reached)")
                self.metrics["capped"] += 1
                return
            
            self.metrics["promoted"] += 1
            is_from_accumulation = event.payload.get("accumulated", False)
            self._create_narrative(event, from_accumulation=is_from_accumulation)
        else:
            # 3. Accumulation Logic - Buffer LOW events
            self.metrics["rejected"] += 1
            synthetic = self.accumulator.add_event(event)
            
            if synthetic:
                # Promotion triggered! Re-process the synthetic event
                logger.info(f"ACCUMULATION_TRIGGERED: Processing synthetic event.")
                self._process_single_event(synthetic, narrative_map)

    def _create_narrative(self, event: Event, from_accumulation: bool = False):
        # Title Generation (Template based)
        title = f"New {event.event_type.value} on {event.asset_id}"
        if event.payload.get('signal_name'):
             title = f"{event.payload['signal_name']} detected on {event.asset_id}"
             
        explanation = {
             "genesis_event": event.event_id,
             "genesis_type": event.event_type.value,
             "from_accumulation": from_accumulation,
             **event.payload # Propagate payload metadata (shadow, context, etc.)
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
        
        # Update daily cap
        self._narratives_today += 1
        
        self.metrics["narratives_created"] += 1
        if from_accumulation:
            self.metrics["narratives_via_accumulation"] += 1
        if event.payload.get("shadow", False):
            self.metrics["shadow"] += 1

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
