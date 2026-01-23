import argparse
import os
import glob

# Layer Definitions
COGNITIVE_LAYERS = ["narratives", "signals", "decision"]
ACTION_LAYERS = ["execution", "adapter", "broker"]

# Dangerous keywords indicative of direct execution logic
DANGEROUS_KEYWORDS = ["place_order", "market_order", "limit_order", ".buy(", ".sell("]

def scan_file(filepath: str, rel_path: str) -> list:
    violations = []
    
    # Determine which layer this file belongs to
    current_layer = None
    for layer in COGNITIVE_LAYERS:
        if layer in rel_path:
            current_layer = layer
            break
            
    # If not in a cognitive layer, skip (e.g. scripts, tests, execution itself)
    if not current_layer:
        return []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith("#"): continue
                
                # Check 1: Illegal Imports
                # e.g. "from src.execution import ..." is bad in strict cognitive layer
                if line.startswith("import ") or line.startswith("from "):
                    for action in ACTION_LAYERS:
                        if f"{action}" in line:
                             violations.append(f"Line {i+1}: Cognitive Layer '{current_layer}' imports Action Layer '{action}'")

                # Check 2: Direct Execution calls
                for dang in DANGEROUS_KEYWORDS:
                    if dang in line:
                        violations.append(f"Line {i+1}: Found potential execution call '{dang}' in Cognitive logic")

    except Exception as e:
        violations.append(f"Error reading {filepath}: {e}")
        
    return violations

def main():
    parser = argparse.ArgumentParser(description="Cognitive Order Validator")
    parser.add_argument("--target", default="src", help="Source root to scan")
    
    args = parser.parse_args()
    root = os.path.abspath(args.target)
    
    report = {}
    
    for ext in ['*.py']:
        for filepath in glob.glob(os.path.join(root, '**', ext), recursive=True):
            rel_path = os.path.relpath(filepath, root).replace("\\", "/") # Unified path
            
            v = scan_file(filepath, rel_path)
            if v:
                report[rel_path] = v
                
    print(f"--- Cognitive Order Validation: {args.target} ---")
    if not report:
        print("PASS: No structural violations found.")
    else:
        print(f"FAIL: Found violations in {len(report)} files.")
        for f, v_list in report.items():
            print(f"\nFile: {f}")
            for v in v_list:
                print(f"  - {v}")

if __name__ == "__main__":
    main()
