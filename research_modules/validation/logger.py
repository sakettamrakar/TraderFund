"""Research Validation - Logger"""
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from research_modules.universe_hygiene import config as uh_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

VALIDATION_LOG_PATH = Path("data") / "validation" / "research_log.csv"

class ValidationLogger:
    """Logs snapshot of narrative states for validation."""
    
    def log_validation_snapshot(self):
        logger.info("VALIDATION LOGGER - Starting snapshot")
        
        # Load all daily narratives
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        daily_path = Path("data") / "narratives" / "us" / date_str
        
        if not daily_path.exists():
            logger.warning("No narratives found for today. Skipping validation log.")
            return

        records = []
        for f in daily_path.glob("*_narrative.parquet"):
            try:
                df = pd.read_parquet(f)
                row = df.iloc[0]
                records.append({
                    "date": date_str,
                    "symbol": row["symbol"],
                    "highest_stage": self._infer_stage(row), # Need logic or explicitly load from elsewhere
                    "narrative_type": row["narrative_type"],
                    "narrative_state": row["narrative_state"],
                    "risk_profile": row.get("risk_context", "unknown")
                })
            except Exception as e:
                logger.error(f"Error reading {f}: {e}")
                
        if records:
            df_log = pd.DataFrame(records)
            VALIDATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            # Append if exists
            write_header = not VALIDATION_LOG_PATH.exists()
            df_log.to_csv(VALIDATION_LOG_PATH, mode='a', header=write_header, index=False)
            logger.info(f"Logged {len(records)} validation records to {VALIDATION_LOG_PATH}")
        else:
            logger.info("No records to log.")
            
    def _infer_stage(self, row) -> int:
        """Infer highest stage from narrative type/state (Heuristic)."""
        state = row["narrative_state"]
        if state == "active_momentum": return 4
        if state == "developing": return 3
        if state == "potential": return 2
        return 0

def log_validation_snapshot():
    """Module-level helper for orchestrator."""
    logger = ValidationLogger()
    return logger.log_validation_snapshot()
