import sys
import re
import argparse
import datetime
from pathlib import Path

def parse_diff(diff_content):
    """
    Parses a unified diff string and returns structured data.
    """
    files = {}
    current_file = None
    
    file_header_re = re.compile(r'^diff --git a/(.*) b/(.*)')
    chunk_header_re = re.compile(r'^@@ -\d+,\d+ \+(\d+),\d+ @@')
    
    # Simple regex for function definitions in common languages
    func_def_re = re.compile(r'^\+\s*(def |function |func |class |public |private |protected ).*')
    
    lines = diff_content.splitlines()
    
    for line in lines:
        if line.startswith('diff --git'):
            match = file_header_re.match(line)
            if match:
                current_file = match.group(2)
                files[current_file] = {
                    'lines_added': 0,
                    'lines_removed': 0,
                    'type': 'unknown',
                    'api_changes': []
                }
                
                # Determine file type
                if current_file.endswith(('.md', '.txt')):
                    files[current_file]['type'] = 'docs'
                elif current_file.endswith(('.json', '.yaml', '.yml', '.env', '.ini')):
                    files[current_file]['type'] = 'config'
                elif current_file.endswith(('.py', '.js', '.ts', '.go', '.java', '.c', '.cpp', '.h')):
                    files[current_file]['type'] = 'code'
                else:
                    files[current_file]['type'] = 'other'
                    
        elif current_file:
            if line.startswith('+') and not line.startswith('+++'):
                files[current_file]['lines_added'] += 1
                if func_def_re.match(line):
                    files[current_file]['api_changes'].append(line.strip())
            elif line.startswith('-') and not line.startswith('---'):
                files[current_file]['lines_removed'] += 1

    return files

def generate_summary(files):
    print("# Section 1: Observed Changes")
    print(f"**Total Files Changed**: {len(files)}")
    
    for fname, stats in files.items():
        print(f"*   `{fname}` ({stats['type']})")
        print(f"    *   Added: {stats['lines_added']} | Removed: {stats['lines_removed']}")

    print("\n# Section 2: Mechanism")
    for fname, stats in files.items():
        if stats['api_changes']:
            print(f"*   **{fname}**: Detected API surface changes:")
            for change in stats['api_changes']:
                # Truncate long lines for display
                print(f"    *   `{change[:80]}`")
        if stats['lines_added'] > 0 and stats['lines_removed'] == 0:
             print(f"*   **{fname}**: Pure addition (New content/module).")

    print("\n# Section 3: Candidate Impacts")
    impacted_docs = []
    has_code_change = any(s['type'] == 'code' for s in files.values())
    has_config_change = any(s['type'] == 'config' for s in files.values())
    
    if has_code_change:
        impacted_docs.append("docs/epistemic/architecture_overview.md (if structural)")
        impacted_docs.append("Runbooks (if operational)")
    if has_config_change:
        impacted_docs.append("docs/epistemic/active_constraints.md (if limits changed)")
    
    if not impacted_docs:
        print("*   No obvious documentation impacts detected based on file types.")
    else:
        for doc in impacted_docs:
            print(f"*   {doc}")

def generate_draft_did(files):
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    scope = "unknown"
    if files:
        # Heuristic for scope: taking the first directory of the first file or 'misc'
        first_file = next(iter(files))
        parts = first_file.split('/')
        if len(parts) > 1:
            scope = parts[0]
            
    print("\n--- DRAFT DID TEMPLATE ---\n")
    print(f"# Documentation Impact Declaration")
    print("")
    print(f"**Change Summary**: [Human Input Required]")
    
    types = set(s['type'] for s in files.values())
    t_str = " / ".join(sorted([t.capitalize() for t in types]))
    print(f"**Change Type**: {t_str}")
    print("")
    print("## Impact Analysis")
    print("*   **Potentially Impacted Documents**:")
    
    # Repeat impact logic for the DID
    has_code = any(s['type'] == 'code' for s in files.values())
    has_config = any(s['type'] == 'config' for s in files.values())
    
    if has_code:
        print("    *   Runbooks")
        print("    *   Architecture Documentation")
    if has_config:
        print("    *   Configuration Guides")
    if not has_code and not has_config:
        print("    *   [None Detected]")

    print("*   **Impact Nature**: [Describe nature of impact]")
    print("")
    print("## Required Actions")
    print("*   [ ] Update relevant documentation")
    print("")
    print("## Epistemic Impact")
    print("*   **Invariants Affected**: [None / List]")
    print("*   **Constraints Affected**: [None / List]")
    print("")
    print("**Status**: Draft")

def main():
    parser = argparse.ArgumentParser(description="Deterministic Change Summarizer")
    parser.add_argument('diff_file', nargs='?', help='Path to diff file (or stdin if not provided)')
    parser.add_argument('--draft-did', action='store_true', help='Generate Draft DID template')
    
    args = parser.parse_args()
    
    content = ""
    if args.diff_file:
        try:
            with open(args.diff_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File {args.diff_file} not found.")
            sys.exit(1)
    else:
        # Read from stdin
        if not sys.stdin.isatty():
             content = sys.stdin.read()
        else:
            print("Error: No input provided via stdin or argument.")
            sys.exit(1)

    if not content:
        print("Error: Empty diff content.")
        sys.exit(1)

    files = parse_diff(content)
    
    # Failsafe for ambiguity
    if not files:
        print("Error: Could not parse any file changes from the provided diff.")
        sys.exit(1)

    generate_summary(files)
    
    if args.draft_did:
        generate_draft_did(files)

if __name__ == "__main__":
    main()
