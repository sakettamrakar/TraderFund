import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_live_status():
    print("Testing Live System Status...")
    try:
        r = requests.get(f"{BASE_URL}/system/status?market=US")
        r.raise_for_status()
        data = r.json()
        print(f"PASS: Live Status Fetched. Gate: {data.get('gate', {}).get('execution_gate')}")
        return True
    except Exception as e:
        print(f"FAIL: Live Status Error: {e}")
        return False

def test_inspection_scenarios():
    print("\nTesting Inspection Scenarios...")
    try:
        r = requests.get(f"{BASE_URL}/inspection/stress_scenarios")
        r.raise_for_status()
        data = r.json()
        scenarios = data.get('scenarios', [])
        print(f"PASS: Scenarios Fetched. Count: {len(scenarios)}")
        
        # Verify S1-S4 exist
        ids = [s['id'] for s in scenarios]
        expected = ['S1', 'S2', 'S3', 'S4']
        if all(e in ids for e in expected):
            print(f"PASS: All expected scenarios found: {ids}")
        else:
            print(f"FAIL: Missing scenarios. Found: {ids}")
            return False
            
        # Verify structure of S2 (which has both markets)
        s2 = next(s for s in scenarios if s['id'] == 'S2')
        if 'US' in s2['markets'] and 'outcomes' in s2['markets']['US']:
            print("PASS: S2 has US outcomes.")
            return True
        else:
            print(f"FAIL: S2 missing US outcomes. Keys: {s2['markets'].keys()}")
            return False

    except Exception as e:
        print(f"FAIL: Inspection API Error: {e}")
        return False

if __name__ == "__main__":
    live_ok = test_live_status()
    insp_ok = test_inspection_scenarios()
    
    if live_ok and insp_ok:
        print("\nOVERALL VERIFICATION: PASS")
        sys.exit(0)
    else:
        print("\nOVERALL VERIFICATION: FAIL")
        sys.exit(1)
