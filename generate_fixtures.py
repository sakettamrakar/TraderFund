import os
import json
import pandas as pd
from datetime import datetime

base_dir = "data/fixtures"
os.makedirs(f"{base_dir}/raw", exist_ok=True)
os.makedirs(f"{base_dir}/processed", exist_ok=True)
os.makedirs(f"{base_dir}/us", exist_ok=True)

# raw
raw_data = {
    "symbol": "TCS", "exchange": "NSE", "interval": "1m", "timestamp": "2026-05-17T10:00:00Z",
    "open": 100, "high": 105, "low": 95, "close": 102, "volume": 1000, "source": "fixture", "ingestion_ts": "2026-05-17T10:01:00Z"
}
with open(f"{base_dir}/raw/fixture_raw.jsonl", "w") as f:
    f.write(json.dumps(raw_data) + "\n")

# processed
processed_df = pd.DataFrame([{
    "symbol": "TCS", "exchange": "NSE", "timestamp": "2026-05-17T10:00:00Z",
    "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 1000.0
}])
processed_df.to_parquet(f"{base_dir}/processed/fixture_processed.parquet")

# us
us_data = {
    "Meta Data": {},
    "Time Series (Daily)": {
        "2026-05-17": {
            "1. open": "100", "2. high": "105", "3. low": "95", "4. close": "102", "5. volume": "1000"
        }
    }
}
# wait, the validation checks for: {"timestamp", "open", "high", "low", "close", "volume"}
# If it's a dict, it checks `first_value` columns. 
# Let's just write what the US check expects.
# `first_value = next(iter(payload.values()), {})`
# if isinstance(first_value, dict): columns = {"timestamp", "open", "high", "low", "close", "volume"}
# That means if the first value is a dict, it automatically assumes those columns.
with open(f"{base_dir}/us/fixture_us_daily.json", "w") as f:
    f.write(json.dumps(us_data))

print("Fixtures generated.")
