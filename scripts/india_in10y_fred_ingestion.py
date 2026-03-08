"""
India IN10Y FRED Ingestion Script.
Sources real India 10-Year Government Bond Yield from FRED.

DATA PROVENANCE:
- Source: Federal Reserve Bank of St. Louis (FRED)
- Series: INDIRLTLT01STM (India Long-Term Interest Rate)
- Original Source: International Monetary Fund (IMF)
- Frequency: Monthly
- Units: Percent

SECURITY:
- API key read from environment variable FRED_API_KEY
- Key is NEVER logged or persisted
"""
import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, rely on system environment

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "india"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FRED_SERIES_ID = "INDIRLTLT01STM"
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_PUBLIC_CSV_URL = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={FRED_SERIES_ID}"


def get_api_key() -> str:
    """
    Retrieves FRED API key from environment.
    Fails explicitly if not found.
    """
    key = os.environ.get("FRED_API_KEY")
    if not key:
        raise EnvironmentError(
            "FRED_API_KEY environment variable not set. "
            "Cannot proceed with REAL_ONLY data ingestion."
        )
    return key


def fetch_india_10y_yield_from_api(api_key: str) -> pd.DataFrame:
    """
    Fetches India 10Y yield from FRED API.
    """
    params = {
        "series_id": FRED_SERIES_ID,
        "api_key": api_key,  # Used only in request, never logged
        "file_type": "json",
        "observation_start": "2020-01-01",
        "observation_end": datetime.now().strftime("%Y-%m-%d"),
    }
    
    print(f"Fetching FRED series: {FRED_SERIES_ID}")
    response = requests.get(FRED_API_URL, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    observations = data.get("observations", [])
    
    if not observations:
        raise ValueError("No observations returned from FRED API")
    
    # Parse observations
    records = []
    for obs in observations:
        date_str = obs.get("date")
        value_str = obs.get("value")
        
        # FRED returns "." for missing values
        if value_str == "." or not value_str:
            continue
        
        try:
            records.append({
                "Date": pd.to_datetime(date_str),
                "Close": float(value_str)
            })
        except (ValueError, TypeError):
            continue
    
    df = pd.DataFrame(records)
    df = df.sort_values("Date").reset_index(drop=True)
    
    print(f"Retrieved {len(df)} valid observations")
    return df


def fetch_india_10y_yield_from_public_csv() -> pd.DataFrame:
    """
    Fetches India 10Y yield from FRED's public CSV endpoint.
    """
    print(f"Fetching public FRED CSV: {FRED_SERIES_ID}")
    df = pd.read_csv(FRED_PUBLIC_CSV_URL)
    if df.empty:
        raise ValueError("No observations returned from public FRED CSV")

    df = df.rename(columns={"observation_date": "Date", FRED_SERIES_ID: "Close"})
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)
    print(f"Retrieved {len(df)} valid observations")
    return df


def fetch_india_10y_yield(api_key: str | None = None) -> pd.DataFrame:
    if api_key:
        return fetch_india_10y_yield_from_api(api_key)
    return fetch_india_10y_yield_from_public_csv()


def save_in10y(df: pd.DataFrame) -> Path:
    """
    Saves IN10Y data to canonical CSV format.
    """
    output_path = DATA_DIR / "IN10Y.csv"

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna(subset=["Date", "Close"]).drop_duplicates(subset=["Date"], keep="last")
    df = df.sort_values("Date").reset_index(drop=True)
    
    # Remove any existing synthetic file
    if output_path.exists():
        print("Removing existing IN10Y.csv (synthetic placeholder)")
        output_path.unlink()
    
    # Save new real data
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")
    
    return output_path


def ingest_india_10y() -> Path:
    """
    Fetches and persists the canonical real-data IN10Y series.
    """
    try:
        api_key = get_api_key()
        print("API key retrieved from environment (not logged)")
    except EnvironmentError:
        api_key = None
        print("FRED_API_KEY not set. Falling back to public FRED CSV endpoint.")

    df = fetch_india_10y_yield(api_key)
    return save_in10y(df)


def main():
    print("=" * 60)
    print("INDIA IN10Y FRED INGESTION")
    print("=" * 60)
    print(f"Series: {FRED_SERIES_ID}")
    print(f"Source: FRED (IMF via St. Louis Fed)")
    print(f"Provenance: REAL")
    print()
    
    try:
        output_path = ingest_india_10y()
        df = pd.read_csv(output_path, parse_dates=["Date"])
        
        # Validate minimum history
        if len(df) < 50:
            print(f"WARNING: Only {len(df)} observations. Minimum 100 recommended.")
        
        print()
        print("=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print(f"Output: {output_path}")
        print(f"Rows: {len(df)}")
        print(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"Latest Yield: {df['Close'].iloc[-1]:.2f}%")
        
        return True
    except requests.RequestException as e:
        print(f"API ERROR: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
