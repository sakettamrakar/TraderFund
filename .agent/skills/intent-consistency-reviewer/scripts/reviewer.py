import argparse
import os
import glob
from pathlib import Path
from typing import List, Dict

# Forbidden patterns that violate Project Intent
# In a full implementation, these could represent regexes or be loaded from project_intent.md
FORBIDDEN_PATTERNS = [
    "black box",
    "neural network", 
    "deep learning",
    "high frequency",
    "hft",
    "arbitrage",
    "predict_price", # We identify regimes, we don't predict scalar prices
    "ignore_context"
]

def scan_file(filepath: str) -> List[str]:
    """Scan a single file for forbidden patterns."""
    violations = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                line_lower = line.lower()
                for pattern in FORBIDDEN_PATTERNS:
                    if pattern in line_lower:
                        violations.append(f"Line {i+1}: Found forbidden term '{pattern}'")
    except Exception as e:
        violations.append(f"Error reading file: {str(e)}")
    return violations

def main():
    parser = argparse.ArgumentParser(description="Intent Consistency Reviewer")
    parser.add_argument("--target", required=True, help="File or directory to scan")
    
    args = parser.parse_args()
    target = args.target
    
    report = {}
    
    if os.path.isfile(target):
        v = scan_file(target)
        if v: report[target] = v
    elif os.path.isdir(target):
        # Recursive scan of python/md files
        for ext in ['*.py', '*.md', '*.json']:
            for filepath in glob.glob(os.path.join(target, '**', ext), recursive=True):
                v = scan_file(filepath)
                if v: report[filepath] = v
    else:
        print(f"Error: Target {target} not found.")
        return

    # Output Report
    print(f"--- Intent Consistency Report: {target} ---")
    if not report:
        print("PASS: No intent violations found.")
    else:
        print(f"FAIL: Found violations in {len(report)} files.")
        for f, v_list in report.items():
            print(f"\nFile: {f}")
            for v in v_list:
                print(f"  - {v}")

if __name__ == "__main__":
    main()
