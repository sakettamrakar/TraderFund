import requests
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.port_manager import get_api_base_url


BASE_URL = get_api_base_url()

def check_market(market):
    print(f"--- CHECKING MARKET: {market} ---")
    try:
        # Snapshot
        r_snap = requests.get(f"{BASE_URL}/market/snapshot", params={"market": market})
        if r_snap.status_code == 200:
            data = r_snap.json()
            print(f"RAW SNAPSHOT: {json.dumps(data)}")
        else:
            print(f"SNAPSHOT FAILED: {r_snap.status_code} {r_snap.text}")

        # Macro
        r_macro = requests.get(f"{BASE_URL}/macro/context", params={"market": market})
        if r_macro.status_code == 200:
            data = r_macro.json()
            print(f"MACRO [Policy]: {data.get('monetary', {}).get('policy_stance')}")
            print(f"MACRO [Rate]: {data.get('monetary', {}).get('rate_level')}")
        else:
            print(f"MACRO FAILED: {r_macro.status_code} {r_macro.text}")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    print("\n")

if __name__ == "__main__":
    check_market("US")
    check_market("INDIA")
