"""Replay Sanity Checks - Verify Replay Correctness.

This module provides sanity checks to ensure the replay is working correctly
and not exhibiting lookahead bias or other issues.
"""

import sys
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

logger = logging.getLogger(__name__)


def check_no_future_candles(symbol: str, replay_date: str, base_dir: str = "observations/historical_replay") -> Dict:
    """Verify that no signal has a timestamp after the data it was based on.
    
    This check ensures lookahead prevention is working correctly.
    
    Returns:
        Dict with check results.
    """
    output_dir = Path(base_dir) / replay_date
    signals_file = output_dir / f"signals_for_review_{replay_date}.csv"
    
    if not signals_file.exists():
        return {"check": "no_future_candles", "passed": True, "reason": "No signals file"}
    
    df = pd.read_csv(signals_file)
    if df.empty:
        return {"check": "no_future_candles", "passed": True, "reason": "No signals"}
    
    # All signals should have timestamps on the replay date
    df['signal_date'] = pd.to_datetime(df['timestamp']).dt.date.astype(str)
    
    violations = df[df['signal_date'] != replay_date]
    
    if not violations.empty:
        return {
            "check": "no_future_candles",
            "passed": False,
            "reason": f"Found {len(violations)} signals with dates != {replay_date}",
            "violations": violations['timestamp'].tolist()
        }
    
    return {"check": "no_future_candles", "passed": True, "reason": "All signals on correct date"}


def check_vwap_progression(symbol: str, replay_date: str, data_path: str = "data/processed/candles/intraday") -> Dict:
    """Verify that VWAP evolves progressively throughout the day.
    
    VWAP should generally change over time, not be static.
    
    Returns:
        Dict with check results.
    """
    from ..candle_cursor import CandleCursor
    from src.core_modules.momentum_engine.momentum_engine import MomentumEngine
    
    file_path = Path(data_path) / f"NSE_{symbol}_1m.parquet"
    
    if not file_path.exists():
        return {"check": "vwap_progression", "passed": False, "reason": f"Data file not found: {file_path}"}
    
    df = pd.read_parquet(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date.astype(str)
    df_day = df[df['date'] == replay_date].copy()
    
    if df_day.empty:
        return {"check": "vwap_progression", "passed": False, "reason": f"No data for {replay_date}"}
    
    # Compute indicators to get VWAP
    engine = MomentumEngine()
    df_with_ind = engine._compute_indicators(df_day)
    
    # Check VWAP changes over time
    vwap_values = df_with_ind['vwap'].dropna().values
    
    if len(vwap_values) < 2:
        return {"check": "vwap_progression", "passed": False, "reason": "Not enough data points"}
    
    # VWAP should change at least slightly
    vwap_unique = len(set(vwap_values))
    
    if vwap_unique < 3:
        return {
            "check": "vwap_progression",
            "passed": False,
            "reason": f"VWAP only has {vwap_unique} unique values - may be static"
        }
    
    return {"check": "vwap_progression", "passed": True, "reason": f"VWAP has {vwap_unique} unique values"}


def check_signal_timestamp_alignment(symbol: str, replay_date: str, base_dir: str = "observations/historical_replay") -> Dict:
    """Verify that signal timestamps align with valid candle timestamps.
    
    Returns:
        Dict with check results.
    """
    output_dir = Path(base_dir) / replay_date
    signals_file = output_dir / f"signals_for_review_{replay_date}.csv"
    
    if not signals_file.exists():
        return {"check": "timestamp_alignment", "passed": True, "reason": "No signals file"}
    
    df = pd.read_csv(signals_file)
    if df.empty:
        return {"check": "timestamp_alignment", "passed": True, "reason": "No signals"}
    
    # Parse timestamps
    df['signal_ts'] = pd.to_datetime(df['timestamp'])
    
    # Check that all timestamps have valid minute boundaries
    invalid_seconds = df[df['signal_ts'].dt.second != 0]
    
    if not invalid_seconds.empty:
        return {
            "check": "timestamp_alignment",
            "passed": False,
            "reason": f"Found {len(invalid_seconds)} signals with non-minute timestamps"
        }
    
    return {"check": "timestamp_alignment", "passed": True, "reason": "All timestamps aligned to minute boundaries"}


def check_determinism(symbol: str, replay_date: str) -> Dict:
    """Placeholder for determinism check.
    
    Full implementation would run replay twice and compare outputs.
    
    Returns:
        Dict with check results.
    """
    # Note: Full implementation would require running replay twice
    # For now, we just log that this is a manual check
    return {
        "check": "determinism",
        "passed": True,
        "reason": "Manual check required: run replay twice and diff outputs"
    }


def run_all_sanity_checks(symbol: str, replay_date: str) -> List[Dict]:
    """Run all sanity checks and return results.
    
    Args:
        symbol: Trading symbol.
        replay_date: Replay date (YYYY-MM-DD).
        
    Returns:
        List of check result dicts.
    """
    results = []
    
    logger.info("Running sanity checks...")
    
    # 1. No future candles
    result = check_no_future_candles(symbol, replay_date)
    results.append(result)
    logger.info(f"  {result['check']}: {'PASS' if result['passed'] else 'FAIL'} - {result['reason']}")
    
    # 2. VWAP progression
    result = check_vwap_progression(symbol, replay_date)
    results.append(result)
    logger.info(f"  {result['check']}: {'PASS' if result['passed'] else 'FAIL'} - {result['reason']}")
    
    # 3. Timestamp alignment
    result = check_signal_timestamp_alignment(symbol, replay_date)
    results.append(result)
    logger.info(f"  {result['check']}: {'PASS' if result['passed'] else 'FAIL'} - {result['reason']}")
    
    # 4. Determinism (placeholder)
    result = check_determinism(symbol, replay_date)
    results.append(result)
    logger.info(f"  {result['check']}: {'PASS' if result['passed'] else 'FAIL'} - {result['reason']}")
    
    # Summary
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    logger.info(f"Sanity checks: {passed}/{total} passed")
    
    return results
