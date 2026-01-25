import argparse
import logging
from pathlib import Path

from signals.core.enums import Market
from narratives.repository.parquet_repo import ParquetNarrativeRepository
from presentation.summarization.engine import NarrativeSummarizer
from presentation.repository.parquet_repo import ParquetSummaryRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SummaryRunner")

def run_summaries(market_str: str):
    market = Market(market_str)
    base_data = Path("data")
    
    # Repos
    narr_repo = ParquetNarrativeRepository(base_data / "narratives")
    sum_repo = ParquetSummaryRepository(base_data / "presentation/summaries")
    
    # Engine
    summarizer = NarrativeSummarizer(sum_repo)
    
    # 1. Fetch Active Narratives
    logger.info(f"Fetching active narratives for {market.value}...")
    active_narratives = narr_repo.get_active_narratives(market)
    logger.info(f"Found {len(active_narratives)} active narratives.")
    
    if not active_narratives:
        logger.info("No narratives to summarize. Exiting.")
        return

    # 2. Process Summaries
    count = 0
    for narr in active_narratives:
        # Check if summary already exists for this version (optional optimization)
        # For now, always re-generate to update local state
        summarizer.generate_summary(narr)
        count += 1
            
    logger.info(f"Summarization complete. Processed {count} narratives.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TraderFund Narrative Summary Runner")
    parser.add_argument("--market", type=str, default="US", choices=["US", "INDIA"], help="Target market")
    args = parser.parse_args()
    
    run_summaries(args.market)
