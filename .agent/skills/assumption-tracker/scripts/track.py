import argparse
import datetime

LEDGER_PATH = "docs/epistemic/ledger/assumption_changes.md"

def append_assumption(assumption: str, reason: str):
    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    
    entry = f"""
## [{date_str}] Invalidated: {assumption}
*   **Reason**: {reason}
*   **Outcome**: Permanent Constraint.
"""
    
    with open(LEDGER_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)
        
    print(f"Invalidated Assumption: {assumption}")

def main():
    parser = argparse.ArgumentParser(description="Assumption Tracker")
    parser.add_argument("--assumption", required=True, help="The assumption that failed")
    parser.add_argument("--reason", required=True, help="Why it failed (Evidence)")
    
    args = parser.parse_args()
    append_assumption(args.assumption, args.reason)

if __name__ == "__main__":
    main()
