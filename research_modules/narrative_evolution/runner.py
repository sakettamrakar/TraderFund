"""Narrative Evolution - Runner"""
import argparse, json, logging, sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import pandas as pd
from . import config
from .models import Narrative, StageEvidence
from .generator import NarrativeGenerator
from .evolution import NarrativeEvolver

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

def load_stage_data(symbol: str, date_str: str) -> StageEvidence:
    """Load all stage outputs for a symbol."""
    evidence = StageEvidence()
    
    # Stage 1: Structural
    path = config.STRUCTURAL_PATH / date_str / f"{symbol}_capability.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        evidence.structural_score = float(df["structural_capability_score"].iloc[0])
    
    # Stage 2: Energy
    path = config.ENERGY_PATH / date_str / f"{symbol}_energy.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        evidence.energy_score = float(df["energy_setup_score"].iloc[0])
    
    # Stage 3: Participation
    path = config.PARTICIPATION_PATH / date_str / f"{symbol}_trigger.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        evidence.participation_score = float(df["participation_score"].iloc[0])
    
    # Stage 4: Momentum
    path = config.MOMENTUM_PATH / date_str / f"{symbol}_momentum.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        evidence.momentum_score = float(df["momentum_score"].iloc[0])
    
    # Stage 5: Sustainability
    path = config.SUSTAINABILITY_PATH / date_str / f"{symbol}_risk.parquet"
    if path.exists():
        df = pd.read_parquet(path)
        evidence.risk_score = float(df["failure_risk_score"].iloc[0])
        evidence.risk_profile = df["risk_profile"].iloc[0]
    
    return evidence

def load_previous_narrative(symbol: str, date_str: str) -> Optional[Narrative]:
    """Load previous day's narrative for evolution tracking."""
    # For now, return None (no history). In production, would load from prior date.
    return None

def save_narrative(narrative: Narrative, date_str: str):
    """Save narrative to parquet."""
    out_dir = config.NARRATIVE_PATH / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([narrative.to_dict()]).to_parquet(
        out_dir / f"{narrative.symbol}_narrative.parquet", index=False
    )

def run_narrative_generation(symbols: Optional[List[str]] = None, 
                             dry_run: bool = False) -> List[Narrative]:
    logger.info("=" * 60)
    logger.info("NARRATIVE EVOLUTION LAYER - Starting")
    logger.info("=" * 60)
    
    if not symbols:
        from research_modules.universe_hygiene import config as uh
        if uh.ELIGIBILITY_OUTPUT_PATH.exists():
            df = pd.read_parquet(uh.ELIGIBILITY_OUTPUT_PATH)
            symbols = df[df["eligibility_status"] == "eligible"]["symbol"].tolist()
    
    if not symbols:
        logger.error("No symbols")
        return []
    
    generator = NarrativeGenerator()
    evolver = NarrativeEvolver()
    results = []
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    for i, sym in enumerate(symbols):
        logger.info(f"[{i+1}/{len(symbols)}] {sym}...")
        
        evidence = load_stage_data(sym, date_str)
        previous = load_previous_narrative(sym, date_str)
        
        narrative = generator.generate(sym, evidence, previous)
        narrative = evolver.evolve(narrative, previous, evidence)
        
        results.append(narrative)
        logger.info(f"  → {narrative.narrative_type} [{narrative.narrative_state}]")
        logger.info(f"    {narrative.narrative_summary[:80]}...")
        
        if not dry_run:
            save_narrative(narrative, date_str)
    
    logger.info("=" * 60)
    logger.info("NARRATIVE SUMMARY")
    for r in results:
        logger.info(f"  {r.symbol}: {r.narrative_type} [{r.narrative_state}] {r.risk_context}")
    logger.info("=" * 60)
    
    if not results:
        return {"status": "NO_OP", "reason": "no narratives generated"}
    return {"status": "SUCCESS"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--symbols", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    if not args.generate:
        parser.print_help()
        sys.exit(0)
    
    symbols = args.symbols.split(",") if args.symbols else None
    results = run_narrative_generation(symbols, args.dry_run)
    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))

if __name__ == "__main__":
    main()
