"""
Market Story Shadow Runner.

This script executes the Market Story Adapter in SHADOW MODE.
It fetches (mock) stories and feeds them into the NarrativeGenesisEngine.
"""

import sys
import os
import logging
from datetime import datetime

# Ensure project root is in path
sys.path.append(os.getcwd())

from traderfund.narrative.adapters.market_story_adapter import MarketStoryAdapter, MarketStory
from narratives.genesis.engine import NarrativeGenesisEngine
from narratives.repository.base import NarrativeRepository
from narratives.core.models import Narrative
from signals.core.enums import Market

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("MarketStoryRunner")

# Mock Repository for capturing output (similar to synthetic injector)
class InMemoryCaptureRepository(NarrativeRepository):
    def __init__(self):
        self.saved_narratives = []

    def save_narrative(self, narrative: Narrative) -> None:
        # Check if update
        existing = next((n for n in self.saved_narratives if n.narrative_id == narrative.narrative_id), None)
        if existing:
            self.saved_narratives.remove(existing)
        self.saved_narratives.append(narrative)

    def get_narrative_history(self, narrative_id: str): return []
    def get_active_narratives(self, market: Market): return []

def get_mock_market_stories():
    """Simulate fetching normalized stories from News Repo."""
    now = datetime.utcnow().isoformat()
    return [
        MarketStory(
            id="EXT-001",
            headline="Global supply chains verify recovery",
            summary="Shipping rates normalize continuously.",
            published_at=now,
            category="MARKET_SUMMARY",
            region="GLOBAL",
            severity_hint="MEDIUM",
            source="Reuters"
        ),
        MarketStory(
            id="EXT-002",
            headline="Emerging markets see capital outflows",
            summary="Strong dollar puts pressure on EM currencies.",
            published_at=now,
            category="MARKET_SUMMARY",
            region="GLOBAL",
            severity_hint="HIGH",
            source="Bloomberg"
        ),
         MarketStory(
            id="EXT-003",
            headline="Tech sector consolidation continues",
            summary="M&A activity picks up in software.",
            published_at=now,
            category="MARKET_SUMMARY",
            region="US",
            severity_hint="LOW",
            source="TechCrunch"
        )
    ]

def main():
    print("="*60)
    print(" MARKET STORY ADAPTER (SHADOW RUN)")
    print("="*60)
    
    # 1. Setup
    # Use InMemory to avoid polluting DB during this run/test, 
    # BUT the requirements say "Persisted, Logged". 
    # If we want to simulate prod, we'd use valid repo. 
    # However, to see OUTPUT in console easily without querying DB, InMemory is best for verification.
    # The Prompt said "Rely on existing RegimeEnforcedRepository".
    # Engine wraps whatever repo we give it.
    repo = InMemoryCaptureRepository()
    engine = NarrativeGenesisEngine(repo=repo) # Auto-wraps with RegimeEnforcedRepository
    adapter = MarketStoryAdapter(engine)
    
    # 2. Fetch Stories
    stories = get_mock_market_stories()
    print(f">>> Fetched {len(stories)} market stories.")
    
    # 3. Ingest
    print(">>> Ingesting via Adapter...")
    count = adapter.ingest_stories(stories)
    print(f">>> Adapter processed {count} stories.")
    
    # 4. Audit Output
    print("\n" + "="*60)
    print(" SHADOW NARRATIVE AUDIT")
    print("="*60)
    
    if not repo.saved_narratives:
        print("!! NO NARRATIVES GENERATED !!")
        return

    for n in repo.saved_narratives:
        # Extract regime metadata
        meta = n.explainability_payload.get('regime_enforcement', {})
        
        print(f"HEADLINE:     {n.title}")
        
        if meta:
            print(f"REGIME:       {meta.get('regime')}")
            print(f"BIAS:         {meta.get('regime_bias')}")
            print(f"REGIME CONF:  {meta.get('regime_confidence')}")
            print(f"NARR CONF:    {meta.get('narrative_confidence')}")
            print(f"LIFECYCLE:    {meta.get('regime_lifecycle')}")
            print(f"ORIG WEIGHT:  {meta.get('original_weight')}")
            print(f"FINAL WEIGHT: {meta.get('final_weight')}")
            print(f"REASON:       {meta.get('enforcement_reason')}")
            print(f"SHADOW:       {n.explainability_payload.get('shadow', False)}") # Check shadow flag
        else:
            print("REGIME DATA:  [MISSING/NOT ENFORCED]")
            
        print("-" * 60)

if __name__ == "__main__":
    main()
