"""
Synthetic Narrative Injector for Regime Integration Validation.
TEST HARNESS - NOT FOR PRODUCTION USE.

This script feeds synthetic "fake news" events into the real NarrativeGenesisEngine
to verify that the RegimeEnforcedRepository correctly intercepts and adjusts
the resulting narratives based on the active market regime.

It uses an in-memory repository to avoid polluting the production database.
"""

import uuid
import logging
import sys
import os
from datetime import datetime
from typing import List

# Ensure project root is in path
sys.path.append(os.getcwd())

from narratives.core.models import Narrative, Event
from narratives.core.enums import NarrativeState, NarrativeScope, EventType
from narratives.repository.base import NarrativeRepository
from narratives.genesis.engine import NarrativeGenesisEngine
from signals.core.enums import Market

# Configure Logging (Console only for this script)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("SyntheticInjector")

class InMemoryRepository(NarrativeRepository):
    """
    Transient repository for test capture.
    Stores saved narratives in a list for inspection.
    """
    def __init__(self):
        self.saved_narratives: List[Narrative] = []

    def save_narrative(self, narrative: Narrative) -> None:
        # In a real DB, this would upsert.
        # Here we just append or replace for simplicity.
        # To handle updates properly for "Reinforcement", we should replace if ID exists.
        existing_idx = next((i for i, n in enumerate(self.saved_narratives) if n.narrative_id == narrative.narrative_id), -1)
        if existing_idx >= 0:
            self.saved_narratives[existing_idx] = narrative
        else:
            self.saved_narratives.append(narrative)

    def get_narrative_history(self, narrative_id: str) -> List[Narrative]:
        return []

    def get_active_narratives(self, market: Market) -> List[Narrative]:
        # Return empty list to force GENESIS of new narratives for every event
        return []

def create_synthetic_event(headline: str, category: str, severity: float) -> Event:
    """Helper to create a standard valid event."""
    # Map category to event type roughly
    evt_type = EventType.NEWS
    if category.lower() == "macro":
        evt_type = EventType.MACRO
    
    return Event.create(
        etype=evt_type,
        market=Market.US,
        time=datetime.utcnow(),
        severity=severity,
        source="synthetic_injector",
        payload={
            "headline": headline,
            "category": category,
            "summary": f"Synthetic content for: {headline}",
            "signal_name": headline # Using headline as signal name for Genesis title generation
        },
        asset="SYN-USD" # Dummy asset
    )

def main():
    print("="*60)
    print(" SYNTHETIC NARRATIVE INJECTOR (REGIME VALIDATION)")
    print("="*60)
    
    # 1. Setup
    memory_repo = InMemoryRepository()
    
    # Instantiate Engine (Auto-wraps with RegimeEnforcedRepository because enforce_regime=True default)
    print(">>> Initializing NarrativeGenesisEngine...")
    engine = NarrativeGenesisEngine(repo=memory_repo)
    
    # 2. Define Synthetic Stories
    stories = [
        ("Fed hints at rate pause amid slowing inflation", "Macro", 95.0),
        ("Tech earnings beat expectations but guidance remains cautious", "Earnings", 85.0),
        ("Oil prices spike on Middle East tensions", "Geopolitics", 90.0),
        ("Markets remain range-bound despite positive macro data", "Volatility", 70.0), # Low severity might be orphan if < 60, but here 70 is > 60
        ("Unexpected CPI revision increases uncertainty", "Macro", 88.0)
    ]
    
    events = []
    print(f">>> Creating {len(stories)} synthetic events...")
    for headline, cat, score in stories:
        # Create unique asset ID to force separate narratives (otherwise clustering logic might merge them)
        # We want to see distinct outputs for each story.
        evt = create_synthetic_event(headline, cat, score)
        # Hack check: engine uses asset_id for clustering. 
        # If we use same asset_id, they might cluster. 
        # Let's force unique asset_ids for clarity of test.
        # But wait, create_synthetic_event uses "SYN-USD".
        # Let's modify the event after creation or make helper flexible.
        # Actually simplest is just to monkeypatch the asset_id or pass it.
        # But for this test, let's just use unique assets.
        clean_cat = cat.replace(" ", "")
        evt = Event.create(
            etype=evt.event_type, # Use the type determined by helper
            market=Market.US,
            time=datetime.utcnow(),
            severity=score,
            source="synthetic_injector",
            payload={"headline": headline, "signal_name": headline},
            asset=f"SYN-{clean_cat.upper()}"
        )
        events.append(evt)
        
    # 3. Inject
    print(">>> Injecting events into engine...")
    engine.ingest_events(Market.US, events)
    
    # 4. Inspect Results
    print("\n" + "="*60)
    print(" FINAL NARRATIVE AUDIT")
    print("="*60)
    
    if not memory_repo.saved_narratives:
        print("!! NO NARRATIVES GENERATED !!")
        return

    for n in memory_repo.saved_narratives:
        # Extract regime metadata
        meta = n.explainability_payload.get('regime_enforcement', {})
        
        print(f"HEADLINE:     {n.title}")
        
        # Check if regime enforcement occurred
        if meta:
            print(f"REGIME:       {meta.get('regime')}")
            print(f"BIAS:         {meta.get('regime_bias')}")
            print(f"REGIME CONF:  {meta.get('regime_confidence')}")
            print(f"NARR CONF:    {meta.get('narrative_confidence')}")
            print(f"LIFECYCLE:    {meta.get('regime_lifecycle')}")
            print(f"ORIG WEIGHT:  {meta.get('original_weight')}")
            print(f"FINAL WEIGHT: {meta.get('final_weight')}")
            print(f"REASON:       {meta.get('enforcement_reason')}")
        else:
            print("REGIME DATA:  [MISSING/NOT ENFORCED]")
            
        print("-" * 60)

    print("\nPaste the above narrative outputs into the chat for audit.")

if __name__ == "__main__":
    main()
