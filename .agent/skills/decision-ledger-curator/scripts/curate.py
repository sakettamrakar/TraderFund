import argparse
import os
import datetime
import re

LEDGER_PATH = "docs/epistemic/ledger/decisions.md"

def get_next_id(ledger_path: str) -> str:
    """Scan ledger for last [YYYY-MM-DD] Dxxx pattern."""
    if not os.path.exists(ledger_path):
        return "D001"
        
    last_id = 0
    with open(ledger_path, 'r', encoding='utf-8') as f:
        # Check lines for "### [DATE] Dxxx:"
        # Regex: D(\d+)
        content = f.read()
        matches = re.findall(r"D(\d{3}):", content)
        if matches:
            last_id = int(matches[-1]) # Assume chronological
            
    next_id = last_id + 1
    return f"D{next_id:03d}"

def append_decision(ledger_path: str, did: str, title: str, decision: str, rationale: str, impact: str):
    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    
    entry = f"""
---

### [{date_str}] {did}: {title}
**Decision**: {decision}
**Rationale**: {rationale}
**Impacted Documents**: {impact}
"""
    
    with open(ledger_path, 'a', encoding='utf-8') as f:
        f.write(entry)
        
    print(f"Successfully appended decision {did}: {title}")

def main():
    parser = argparse.ArgumentParser(description="Decision Ledger Curator")
    parser.add_argument("--title", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--impact", required=True)
    
    args = parser.parse_args()
    
    # 1. Calculate ID
    next_id = get_next_id(LEDGER_PATH)
    
    # 2. Append
    append_decision(LEDGER_PATH, next_id, args.title, args.decision, args.rationale, args.impact)

if __name__ == "__main__":
    main()
