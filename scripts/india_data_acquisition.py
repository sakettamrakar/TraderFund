"""
India Data Acquisition Script.
Downloads canonical India market proxies from Yahoo Finance.
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "india"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Ticker mappings for Yahoo Finance
INDIA_TICKERS = {
    "NIFTY50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "INDIAVIX": "^INDIAVIX",
}

def download_ticker(name: str, ticker: str, period: str = "2y") -> bool:
    """
    Downloads historical data for a ticker.
    Returns True if successful, False otherwise.
    """
    print(f"Downloading {name} ({ticker})...")
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            print(f"  WARNING: No data returned for {ticker}")
            return False
        
        # Flatten multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # Reset index to have Date as column
        data = data.reset_index()
        
        # Save to CSV
        output_path = DATA_DIR / f"{name}.csv"
        data.to_csv(output_path, index=False)
        print(f"  Saved {len(data)} rows to {output_path}")
        return True
    except Exception as e:
        print(f"  ERROR downloading {ticker}: {e}")
        return False


def create_synthetic_in10y():
    """
    Creates a synthetic IN10Y proxy based on available data.
    NOTE: This is a placeholder. Real RBI data should be used in production.
    For now, we use a static yield approximation for demonstration.
    """
    print("Creating synthetic IN10Y proxy (placeholder)...")
    
    # Generate 200 days of synthetic yield data
    # In reality, this should come from RBI or CCIL
    dates = pd.date_range(end=datetime.now(), periods=200, freq='B')
    
    # Simulate yield around 7% with small variations
    import numpy as np
    np.random.seed(42)
    yields = 7.0 + np.cumsum(np.random.randn(200) * 0.02)
    
    df = pd.DataFrame({
        'Date': dates,
        'Close': yields
    })
    
    output_path = DATA_DIR / "IN10Y.csv"
    df.to_csv(output_path, index=False)
    print(f"  Saved {len(df)} rows to {output_path}")
    print("  WARNING: This is SYNTHETIC data for IN10Y. Replace with real RBI data.")
    return True


def main():
    print("=" * 60)
    print("INDIA DATA ACQUISITION")
    print("=" * 60)
    
    results = {}
    
    # Download real market data
    for name, ticker in INDIA_TICKERS.items():
        success = download_ticker(name, ticker)
        results[name] = "SUCCESS" if success else "FAILED"
    
    # Create synthetic IN10Y (placeholder)
    success = create_synthetic_in10y()
    results["IN10Y"] = "SYNTHETIC" if success else "FAILED"
    
    print("\n" + "=" * 60)
    print("ACQUISITION SUMMARY")
    print("=" * 60)
    for name, status in results.items():
        print(f"  {name}: {status}")
    
    return results


if __name__ == "__main__":
    main()
