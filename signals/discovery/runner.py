import argparse
import logging
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import List

from signals.core.models import Signal
from signals.core.enums import Market, SignalCategory, SignalDirection, SignalState
from signals.repository.parquet_repo import ParquetSignalRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SignalDiscovery")

class MomentumDetector:
    """
    Simple Momentum Detector for Daily Bars.
    """
    def __init__(self, sma_window: int = 20, volume_mult: float = 1.5):
        self.sma_window = sma_window
        self.volume_mult = volume_mult

    def detect(self, symbol: str, df: pd.DataFrame, market: Market) -> List[Signal]:
        if len(df) < self.sma_window:
            return []

        df = df.copy()
        df.sort_index(inplace=True)
        
        df['sma'] = df['close'].rolling(window=self.sma_window).mean()
        df['vol_ma'] = df['volume'].rolling(window=self.sma_window).mean()
        
        latest = df.iloc[-1]
        
        signals = []
        
        # Signal Generation Logic
        price_above_sma = latest['close'] > latest['sma']
        vol_surge = latest['volume'] > (latest['vol_ma'] * self.volume_mult)
        near_high = latest['close'] >= (latest['high'] * 0.98) # Within 2% of day high
        
        if price_above_sma and vol_surge and near_high:
            # Strength on a 0-100 scale
            # Base 70 + volume bonus
            strength = 70.0 + min(30.0, (latest['volume'] / (latest['vol_ma'] * 2)) * 10)
            
            trigger_time = latest.name if isinstance(latest.name, datetime) else datetime.utcnow()
            
            sig = Signal.create(
                name="Daily Momentum",
                market=market,
                asset=symbol,
                category=SignalCategory.MOMENTUM,
                direction=SignalDirection.BULLISH,
                trigger_time=trigger_time,
                horizon="5d",
                expiry_time=datetime.utcnow() + pd.Timedelta(days=5),
                strength=round(strength, 2),
                explanation={
                    "reason": "Price > SMA, Volume Surge, Close near High",
                    "close": float(latest['close']),
                    "sma": float(latest['sma']),
                    "rel_vol": round(float(latest['volume'] / latest['vol_ma']), 2)
                },
                confidence=round(strength, 2)
            )
            signals.append(sig)
            
        return signals

def run_discovery(market_str: str, symbols: List[str] = None):
    market = Market(market_str)
    base_path = Path("data")
    staging_dir = base_path / "staging" / market.value.lower() / "daily"
    signal_repo = ParquetSignalRepository(base_path / "signals")
    
    detector = MomentumDetector()
    
    if not staging_dir.exists():
        logger.error(f"Staging directory not found: {staging_dir}")
        return

    if symbols:
        parquet_files = [staging_dir / f"{s.upper()}.parquet" for s in symbols]
        parquet_files = [f for f in parquet_files if f.exists()]
    else:
        parquet_files = list(staging_dir.glob("*.parquet"))
        
    logger.info(f"Scanning {len(parquet_files)} assets in {market.value}...")
    
    total_signals = 0
    for f in parquet_files:
        symbol = f.stem
        try:
            df = pd.read_parquet(f)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
            elif not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            signals = detector.detect(symbol, df, market)
            for sig in signals:
                active_sig = sig.transition_to(SignalState.ACTIVE)
                signal_repo.save_signal(active_sig)
                total_signals += 1
                logger.info(f"Signal Generated: {symbol} @ {active_sig.trigger_timestamp} (ID: {active_sig.signal_id[:8]})")
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            
    logger.info(f"Discovery complete. Total signals generated: {total_signals}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TraderFund Signal Discovery Runner")
    parser.add_argument("--market", type=str, default="US", choices=["US", "INDIA"], help="Target market")
    parser.add_argument("--symbols", type=str, help="Comma separated symbols (optional)")
    args = parser.parse_args()
    
    symbol_list = args.symbols.split(',') if args.symbols else None
    run_discovery(args.market, symbol_list)
