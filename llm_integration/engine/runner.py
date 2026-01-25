import argparse
import logging
import json
from pathlib import Path
from typing import List

from signals.core.enums import Market
from narratives.repository.parquet_repo import ParquetNarrativeRepository
from llm_integration.engine.explainer import ExplainerEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LLMRunner")

def run_explanations(market_str: str):
    market = Market(market_str)
    base_data = Path("data")
    
    # Repos
    narr_repo = ParquetNarrativeRepository(base_data / "narratives")
    
    # Engine
    engine = ExplainerEngine()
    
    # 1. Fetch Active Narratives
    logger.info(f"Fetching active narratives for {market.value}...")
    active_narratives = narr_repo.get_active_narratives(market)
    logger.info(f"Found {len(active_narratives)} active narratives.")
    
    if not active_narratives:
        logger.info("No narratives to explain. Exiting.")
        return

    # 2. Process Explanations
    for narr in active_narratives:
        logger.info(f"Explaining Narrative: {narr.title} ({narr.narrative_id[:8]})")
        explanation = engine.explain_narrative(narr.to_dict())
        
        if explanation:
            # Print to stdout for visibility (in production this goes to a separate audit log)
            print("-" * 40)
            print(f"HEADLINE: {narr.title}")
            print(f"CONFIDENCE: {explanation.confidence_level}")
            print(f"EXPLANATION:\n{explanation.text}")
            print("-" * 40)
            
    logger.info("LLM Explanation pipeline complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TraderFund LLM Explanation Runner")
    parser.add_argument("--market", type=str, default="US", choices=["US", "INDIA"], help="Target market")
    args = parser.parse_args()
    
    run_explanations(args.market)
