import os
import sys
import json
import logging
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("PatternMatcher")

class PatternMatcher:
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.data_dir = self.root / "data" / "processed" / "candles" # default assumption
        
    def load_history(self, symbol: str) -> pd.DataFrame:
        """Loads historical data for symbol. Mock implementation for prototype."""
        # In a real system, this reads Parquet from data/processed
        # For prototype, we will look for a sample CSV or create synthetic if missing
        
        target_path = self.data_dir / f"{symbol}_daily.parquet"
        if target_path.exists():
            return pd.read_parquet(target_path)
        
        logger.warning(f"History not found at {target_path}. Using synthetic data for demonstration.")
        return self._generate_synthetic_history()

    def _generate_synthetic_history(self) -> pd.DataFrame:
        dates = pd.date_range(end=pd.Timestamp.now(), periods=500, freq='B')
        # Random walk
        prices = 100 + np.cumsum(np.random.normal(0, 1, 500))
        df = pd.DataFrame({
            'timestamp': dates,
            'close': prices,
            'volume': np.random.randint(1000, 5000, 500)
        })
        return df

    def find_matches(self, symbol: str, lookback: int = 5, threshold: float = 0.8):
        logger.info(f"Searching for patterns: Symbol={symbol}, Window={lookback}, Threshold={threshold}")
        
        df = self.load_history(symbol)
        if len(df) < lookback * 2:
            return {"error": "Insufficient data history"}
            
        # Current pattern (last N bars)
        current_pattern = df['close'].iloc[-lookback:].values
        
        # Standardize current pattern for correlation (Z-score mostly, or just normalize to start=0)
        # Using Pearson Correlation on raw series or returns? 
        # Robust approach: Normalize to % change from start of window
        
        def normalize(arr):
            return (arr - np.mean(arr)) / (np.std(arr) + 1e-9)

        current_norm = normalize(current_pattern)
        
        matches = []
        
        # Sliding window over history (excluding current window to avoid self-match)
        history_window = df.iloc[:-lookback]
        
        # Naive loop for prototype clarity (Vectorize for prod)
        for i in range(len(history_window) - lookback):
            window = df['close'].iloc[i : i+lookback].values
            window_norm = normalize(window)
            
            # Corr
            corr = np.corrcoef(current_norm, window_norm)[0, 1]
            
            if corr >= threshold:
                matches.append({
                    "date": df['timestamp'].iloc[i + lookback - 1].strftime('%Y-%m-%d'),
                    "score": round(float(corr), 4),
                    "context_index": i
                })
        
        # Sort by score
        matches = sorted(matches, key=lambda x: x['score'], reverse=True)[:10]
        
        return {
            "symbol": symbol,
            "lookback": lookback,
            "matches_found": len(matches),
            "top_matches": matches
        }

def main():
    parser = argparse.ArgumentParser(description="Pattern Matcher Skill")
    parser.add_argument("--symbol", default="SYNTH")
    parser.add_argument("--lookback", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=0.85)
    
    args = parser.parse_args()
    
    root = Path(os.getcwd())
    matcher = PatternMatcher(root)
    
    result = matcher.find_matches(args.symbol, args.lookback, args.threshold)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
