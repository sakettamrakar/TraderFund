import argparse
import json
import glob
import os
import datetime
from pathlib import Path
from typing import List, Dict, Any

def load_logs(log_dir: str = "logs") -> List[Dict[str, Any]]:
    """Recursively load all JSON logs from directory."""
    records = []
    files = glob.glob(os.path.join(log_dir, "*.json"))
    
    for f in files:
        with open(f, 'r') as fp:
            for line in fp:
                line = line.strip()
                if not line: continue
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError:
                    # Fallback for malformed lines
                    records.append({
                        "timestamp": "UNKNOWN", 
                        "level": "ERROR", 
                        "logger": "System", 
                        "message": f"Malformed Log: {line[:50]}...", 
                        "user": "UNKNOWN"
                    })
    
    # Sort by timestamp
    # Handle mixed timestamp formats if any, but standard is ISO
    records.sort(key=lambda x: x.get("timestamp", ""))
    return records

def print_table(records: List[Dict]):
    """Print simple ASCII table."""
    if not records:
        print("No logs found matching criteria.")
        return

    # Columns: Time, Level, User, Logger, Message
    print(f"{'TIMESTAMP':<28} | {'LEVEL':<8} | {'USER':<15} | {'LOGGER':<20} | {'MESSAGE'}")
    print("-" * 120)
    
    for r in records:
        ts = r.get("timestamp", "")[:26].replace("T", " ") # Truncate/Format
        lvl = r.get("level", "INFO")
        usr = r.get("user", "System")[:15]
        logr = r.get("logger", "")[:20]
        msg = r.get("message", "")
        
        print(f"{ts:<28} | {lvl:<8} | {usr:<15} | {logr:<20} | {msg}")

def main():
    parser = argparse.ArgumentParser(description="Audit Log Viewer")
    parser.add_argument("--dir", default="logs", help="Log directory")
    parser.add_argument("--last", type=int, help="Show last N records")
    parser.add_argument("--user", type=str, help="Filter by user ID")
    parser.add_argument("--day", type=str, help="Filter by date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    all_logs = load_logs(args.dir)
    
    filtered = all_logs
    
    # Filter by Day
    if args.day:
        filtered = [r for r in filtered if r.get("timestamp", "").startswith(args.day)]
        
    # Filter by User
    if args.user:
        filtered = [r for r in filtered if r.get("user") == args.user]
        
    # Filter Last N
    if args.last:
        filtered = filtered[-args.last:]
        
    print_table(filtered)

if __name__ == "__main__":
    main()
