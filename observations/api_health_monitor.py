
import requests
import socket
import time
from datetime import datetime
from pathlib import Path

# API Endpoints to Monitor
ENDPOINTS = {
    "Angel Instrument Master": {
        "url": "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json",
        "type": "GET"
    },
    "Angel SmartAPI": {
        "url": "https://smartapi.angelbroking.com/publisher-login",
        "type": "GET"
    },
    "Angel SmartAPI Trade": {
        "url": "https://smartapi.angelbroking.com/trading-login",
        "type": "GET"
    }
}

HEALTH_FILE = Path("observations/api_health.md")

def check_endpoint(name, config):
    try:
        start = time.time()
        if config["type"] == "HEAD":
            response = requests.head(config["url"], timeout=5)
        else:
            response = requests.get(config["url"], timeout=5)
        
        latency = (time.time() - start) * 1000
        status = "HEALTHY" if response.status_code < 400 else f"ERROR ({response.status_code})"
        
        # Special case for Instrument Master if it fails
        if name == "Angel Instrument Master" and response.status_code >= 400:
             status = "DOWN (Timeout/Server Error)"
             
        return {
            "name": name,
            "status": status,
            "latency": f"{latency:.0f}ms",
            "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except requests.exceptions.Timeout:
        return {
            "name": name,
            "status": "TIMEOUT",
            "latency": ">5000ms",
            "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "name": name,
            "status": f"UNREACHABLE",
            "latency": "N/A",
            "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def update_health_file():
    results = []
    for name, config in ENDPOINTS.items():
        results.append(check_endpoint(name, config))

    # Determine Overall Health
    overall_status = "STABLE"
    if any(r["status"] != "HEALTHY" for r in results):
        overall_status = "DEGRADED"
    if all(r["status"] != "HEALTHY" for r in results):
        overall_status = "CRITICAL"

    content = f"""# System API Health Monitor

**Last System Scan**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Overall Status**: {overall_status}

## Dependent APIs Status

| API Name | Status | Latency | Last Checked |
|----------|--------|---------|--------------|
"""
    for r in results:
        status_color = "🟢" if r["status"] == "HEALTHY" else "🔴"
        if "TIMEOUT" in r["status"] or "ERROR" in r["status"]:
            status_color = "🟡"
            
        content += f"| {r['name']} | {status_color} {r['status']} | {r['latency']} | {r['last_check']} |\n"

    content += """
---
*This file is automatically updated by the Momentum Live Runner every cycle.*
"""

    HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_health_file()
