import sys
import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add project root to path
sys.path.append(os.getcwd())

from narratives.core.models import Event
from narratives.core.enums import EventType, NarrativeScope
from narratives.genesis.engine import NarrativeGenesisEngine
from narratives.repository.parquet_repo import ParquetNarrativeRepository
from signals.core.enums import Market
from src.utils.logging import setup_logging

# Setup Logging
logger = setup_logging("RunNarrativeCLI", log_dir="logs")

def json_to_event(data: Dict) -> Event:
    """Convert a dictionary to an Event object."""
    # Handle Enums
    etype = EventType(data.get("event_type", "SIGNAL"))
    market = Market(data.get("market", "US"))
    
    # Handle DateTime
    ts_str = data.get("timestamp")
    try:
        ts = datetime.fromisoformat(ts_str)
    except:
        ts = datetime.utcnow()
        
    return Event.create(
        etype=etype,
        market=market,
        time=ts,
        severity=float(data.get("severity_score", 0.0)),
        source=data.get("source_reference", "unknown"),
        payload=data.get("payload", {}),
        asset=data.get("asset_id")
    )

def main():
    parser = argparse.ArgumentParser(description="Run Narrative Genesis Engine")
    parser.add_argument("--market", default="US", help="Market to process (US/INDIA)")
    parser.add_argument("--inbox", default="data/events/inbox", help="Directory for input JSON events")
    parser.add_argument("--archive", default="data/events/archive", help="Directory for processed events")
    parser.add_argument("--noregime", action="store_true", help="Disable regime enforcement (TEST ONLY)")
    
    args = parser.parse_args()
    
    market = Market(args.market)
    inbox_path = Path(args.inbox)
    archive_path = Path(args.archive)
    
    if not inbox_path.exists():
        logger.error(f"Inbox path does not exist: {inbox_path}")
        return

    # 1. Initialize Repository
    repo_path = Path("data/narratives")
    repo = ParquetNarrativeRepository(repo_path)
    
    # 2. Initialize Engine
    engine = NarrativeGenesisEngine(repo, enforce_regime=not args.noregime)
    
    # 3. Load Events
    events: List[Event] = []
    processed_files = []
    
    logger.info(f"Scanning {inbox_path} for events...")
    for f in inbox_path.glob("*.json"):
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)
                if isinstance(data, list):
                    for item in data:
                        events.append(json_to_event(item))
                else:
                    events.append(json_to_event(data))
            processed_files.append(f)
        except Exception as e:
            logger.error(f"Failed to process {f}: {e}")
            
    if not events:
        logger.info("No new events found.")
        return

    # 4. Run Genesis
    logger.info(f"Ingesting {len(events)} events...")
    engine.ingest_events(market, events)
    
    # 5. Archive Files
    archive_path.mkdir(parents=True, exist_ok=True)
    for f in processed_files:
        try:
            # f.rename(archive_path / f.name) # Rename might fail across filesystems, generic move
            target = archive_path / f.name
            if target.exists():
                # Timestamp if collision
                target = archive_path / f"{datetime.now().timestamp()}_{f.name}"
            f.rename(target)
        except Exception as e:
            logger.warning(f"Failed to archive {f}: {e}")
            
    logger.info("Narrative run complete.")

if __name__ == "__main__":
    main()
