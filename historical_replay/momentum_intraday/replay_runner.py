"""Replay Runner - Top-Level Orchestration for Historical Replay.

This module ties together all replay components and provides a simple
interface for running complete replay sessions with validation and reporting.
"""

import sys
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

from typing import List, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .replay_controller import ReplayController
from .replay_validator import ReplayValidator
from .validation.replay_sanity_checks import run_all_sanity_checks
from ingestion.api_ingestion.angel_smartapi.config import config as angel_config

logger = logging.getLogger(__name__)


def generate_eod_report(replay_date: str, base_dir: str = "observations/historical_replay"):
    """Generate EOD markdown report for a replayed day.
    
    Args:
        replay_date: The date that was replayed (YYYY-MM-DD).
        base_dir: Base directory for replay outputs.
    """
    output_dir = Path(base_dir) / replay_date
    review_file = output_dir / f"signals_for_review_{replay_date}.csv"
    
    if not review_file.exists():
        logger.warning(f"No signals file found for {replay_date}")
        return
    
    df = pd.read_csv(review_file)
    if df.empty:
        logger.info("No signals to summarize")
        return
    
    total_signals = len(df)
    
    # Map outcomes to quality buckets
    def classify_bucket(row):
        outcome = str(row.get('outcome', ''))
        vol = str(row.get('volume_continuation', ''))
        
        if outcome == "Clean" and vol == "Surge":
            return "A"
        elif outcome == "Clean":
            return "B"
        elif outcome == "Choppy":
            return "C"
        else:
            return "D"
    
    df['quality_bucket'] = df.apply(classify_bucket, axis=1)
    buckets = df['quality_bucket'].value_counts().to_dict()
    
    # Calculate insights
    false_signals = df[df['outcome'] == "False"]
    symbol_failures = false_signals['symbol'].value_counts().head(3).to_dict()
    
    avg_conf_success = df[df['outcome'] == "Clean"]['confidence'].mean()
    avg_conf_failure = df[df['outcome'] == "False"]['confidence'].mean()
    
    avg_conf_success_str = f"{avg_conf_success:.2f}" if pd.notna(avg_conf_success) else "N/A"
    avg_conf_failure_str = f"{avg_conf_failure:.2f}" if pd.notna(avg_conf_failure) else "N/A"
    
    summary_content = f"""# HISTORICAL INTRADAY REPLAY — NOT LIVE
# End-of-Day Signal Review: {replay_date}

> ⚠️ **WARNING**: This is a HISTORICAL REPLAY report, NOT live observation data.
> Do not use this for trading decisions or optimization.

## Summary Metrics
- **Mode**: HISTORICAL_REPLAY
- **Total Signals Generated**: {total_signals}
- **Quality Distribution**:
  - Bucket A (High Quality): {buckets.get('A', 0)}
  - Bucket B (Moderate Quality): {buckets.get('B', 0)}
  - Bucket C (Choppy/No Follow-through): {buckets.get('C', 0)}
  - Bucket D (Failure/False Signal): {buckets.get('D', 0)}

## Performance Insights
- **Top Failing Symbols**: {", ".join([f"{k} ({v})" for k, v in symbol_failures.items()]) if symbol_failures else "None"}
- **Avg Confidence of Successes**: {avg_conf_success_str}
- **Avg Confidence of Failures**: {avg_conf_failure_str}

## Diagnostic Learnings (Manual Entry)
1. [Learning 1: Pattern observations from replay]
2. [Learning 2: Signal timing analysis]
3. [Learning 3: Volume behavior notes]

## Replay Metadata
- **Generated**: {datetime.now().isoformat()}
- **Source**: Historical Intraday Momentum Replay
- **Purpose**: Diagnostic analysis only
"""
    
    report_path = output_dir / f"eod_report_{replay_date}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(summary_content)
    
    logger.info(f"EOD report generated: {report_path}")


def run_replay(
    symbol: str,
    replay_date: str,
    interval_minutes: int = 1,
    run_sanity_checks: bool = True
) -> dict:
    """Run a complete historical replay session.
    
    Args:
        symbol: Trading symbol to replay.
        replay_date: Date to replay (YYYY-MM-DD format).
        interval_minutes: Evaluation interval in minutes.
        run_sanity_checks: Whether to run sanity checks after replay.
        
    Returns:
        Dict with replay results.
    """
    logger.info(f"="*60)
    logger.info(f"HISTORICAL INTRADAY MOMENTUM REPLAY")
    logger.info(f"Symbol: {symbol}, Date: {replay_date}, Interval: {interval_minutes}m")
    logger.info(f"="*60)
    
    # Run replay
    controller = ReplayController(
        symbol=symbol,
        replay_date=replay_date,
        interval_minutes=interval_minutes
    )
    
    results = controller.run()
    
    # Generate EOD report
    generate_eod_report(replay_date)
    
    # Run sanity checks
    if run_sanity_checks:
        logger.info("Running sanity checks...")
        sanity_results = run_all_sanity_checks(symbol, replay_date)
        results["sanity_checks"] = sanity_results
    
    logger.info(f"="*60)
    logger.info(f"REPLAY COMPLETE")
    logger.info(f"Signals: {results['signals_generated']}, Output: {results['output_file']}")
    logger.info(f"="*60)
    
    return results


def run_batch_replay(
    symbols: List[str],
    dates: List[str],
    interval_minutes: int = 1,
    run_sanity_checks: bool = True
) -> dict:
    """Run replay for multiple symbols and multiple dates.
    
    Args:
        symbols: List of symbols (or ['ALL'] to use watchlist).
        dates: List of dates in YYYY-MM-DD format.
        interval_minutes: Evaluation interval.
        run_sanity_checks: Whether to run sanity checks.
        
    Returns:
        Summary of batch results.
    """
    if symbols == ['ALL'] or symbols == 'ALL':
        symbols = angel_config.symbol_watchlist

    logger.info(f"Starting batch replay for {len(symbols)} symbols over {len(dates)} dates")
    
    batch_results = {
        "dates_processed": len(dates),
        "symbols_processed": len(symbols),
        "total_signals": 0,
        "results": []
    }

    for current_date in dates:
        logger.info(f"\n>>> PROCESSING DATE: {current_date} <<<")
        for symbol in symbols:
            try:
                result = run_replay(
                    symbol=symbol,
                    replay_date=current_date,
                    interval_minutes=interval_minutes,
                    run_sanity_checks=run_sanity_checks
                )
                batch_results["total_signals"] += result.get("signals_generated", 0)
                batch_results["results"].append(result)
            except Exception as e:
                logger.error(f"Error replaying {symbol} on {current_date}: {e}")
                batch_results["results"].append({
                    "symbol": symbol,
                    "date": current_date,
                    "error": str(e)
                })

    logger.info(f"Batch replay complete. Total signals generated: {batch_results['total_signals']}")
    return batch_results
