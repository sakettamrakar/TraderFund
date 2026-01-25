import argparse
import datetime

LEDGER_PATH = "docs/epistemic/ledger/evolution_log.md"

def append_entry(scope: str, summary: str):
    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    
    # Simple list format as per existing log
    entry = f"- **[{date_str}] [{scope}]**: {summary}\n"
    
    with open(LEDGER_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)
        
    print(f"Recorded Evolution: {scope} - {summary}")

def main():
    parser = argparse.ArgumentParser(description="Evolution Recorder")
    parser.add_argument("--scope", required=True, choices=["Code", "Data", "Ops", "Cognition"], help="Change Scope")
    parser.add_argument("--summary", required=True, help="Short description")
    
    args = parser.parse_args()
    append_entry(args.scope, args.summary)

if __name__ == "__main__":
    main()
