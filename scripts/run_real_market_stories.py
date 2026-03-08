"""
Run Real Market Stories (Integration Test).

FETCHES FROM: managed dashboard API /api/public/market-stories
PIPES TO:    NarrativeGenesisEngine (Shadow Mode)
"""

import sys
import os
import logging
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from traderfund.narrative.adapters.market_story_adapter import MarketStoryAdapter
from narratives.genesis.engine import NarrativeGenesisEngine
from narratives.repository.base import NarrativeRepository
from narratives.core.models import Narrative
from signals.core.enums import Market
from utils.port_manager import get_api_base_url

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("RealMarketStoryRunner")

# Lightweight In-Memory Repo for Verification Output
class AuditRepository(NarrativeRepository):
    def __init__(self):
        self.saved = []
    def save_narrative(self, n: Narrative):
        existing = next((x for x in self.saved if x.narrative_id == n.narrative_id), None)
        if existing: self.saved.remove(existing)
        self.saved.append(n)
    def get_narrative_history(self, nid): return []
    def get_active_narratives(self, mkt): return []

def main():
    API_URL = get_api_base_url(include_api_prefix=True) + "/public/market-stories?limit=10"

    print("="*60)
    print(" REAL MARKET STORY INGESTION")
    print("="*60)
    
    # 1. Setup
    repo = AuditRepository()
    engine = NarrativeGenesisEngine(repo=repo) # Auto-wraps
    engine.MIN_SEVERITY_FOR_GENESIS = 30.0 # Force genesis for explanation
    adapter = MarketStoryAdapter(engine)
    
    # 2. Fetch
    print(f">>> Fetching from {API_URL} ...")
    stories = adapter.fetch_stories_from_api(API_URL)
    
    if not stories:
        print("!! NO STORIES FETCHED !! (Is the server running?)")
    else:
        print(f">>> Fetched {len(stories)} stories.")
    
    # 3. Ingest
    print(">>> Ingesting via Adapter...")
    count = adapter.ingest_stories(stories)
    print(f">>> Ingested {count} narratives.")
    
    # 4. Audit
    print("\n" + "="*60)
    print(" REPO STATE AUDIT")
    print("="*60)
    
    if not repo.saved:
        print("!! NO NARRATIVES IN REPO !!")
        return

    for n in repo.saved:
        meta = n.explainability_payload.get('regime_enforcement', {})
        shadow = n.explainability_payload.get('shadow', False)
        
        print(f"HEADLINE:     {n.title}")
        print(f"REGIME:       {meta.get('regime', 'MISSING')}")
        print(f"BIAS:         {meta.get('regime_bias', 'MISSING')}")
        print(f"REGIME CONF:  {meta.get('regime_confidence', 'N/A')}")
        print(f"NARR CONF:    {meta.get('narrative_confidence', 'N/A')}")
        print(f"FINAL WEIGHT: {meta.get('final_weight', 'N/A')}")
        print(f"REASON:       {meta.get('enforcement_reason', 'N/A')}")
        print(f"SHADOW:       {shadow}")
        print("-" * 60)

if __name__ == "__main__":
    main()
