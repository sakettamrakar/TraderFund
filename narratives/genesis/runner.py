import argparse
import logging
from pathlib import Path
from typing import List

from signals.core.enums import Market
from signals.repository.parquet_repo import ParquetSignalRepository
from narratives.core.models import Event, Narrative
from narratives.core.enums import EventType
from narratives.genesis.engine import NarrativeGenesisEngine
from narratives.repository.parquet_repo import ParquetNarrativeRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NarrativeGenesisRunner")

def run_genesis(market_str: str):
    market = Market(market_str)
    base_data = Path("data")
    
    # Repos
    sig_repo = ParquetSignalRepository(base_data / "signals")
    narr_repo = ParquetNarrativeRepository(base_data / "narratives")
    
    # Engine
    engine = NarrativeGenesisEngine(narr_repo)
    
    # 1. Fetch Active Signals
    logger.info(f"Scanning for active signals in {market.value}...")
    active_signals = sig_repo.get_active_signals(market)
    logger.info(f"Found {len(active_signals)} active signals.")
    
    if not active_signals:
        logger.info("No signals found for narrative clustering. Exiting.")
        return

    # 2. Convert Signals to Events
    events = []
    for sig in active_signals:
        event = Event.create(
            etype=EventType.SIGNAL,
            market=sig.market,
            time=sig.trigger_timestamp,
            severity=sig.raw_strength, # Map Signal strength to Event severity
            source=f"signal:{sig.signal_id}",
            payload={
                "signal_name": sig.signal_name,
                "category": sig.signal_category.value,
                "direction": sig.direction.value,
                "explanation": sig.explainability_payload
            },
            asset=sig.asset_id
        )
        events.append(event)
        
    # 3. Run Narrative Clustering & Genesis
    logger.info(f"Processing {len(events)} events through Narrative Engine...")
    engine.ingest_events(market, events)
    
    logger.info("Narrative Genesis pipeline complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TraderFund Narrative Genesis Runner")
    parser.add_argument("--market", type=str, default="US", choices=["US", "INDIA"], help="Target market")
    args = parser.parse_args()
    
    run_genesis(args.market)
