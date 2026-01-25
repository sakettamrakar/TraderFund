import sys
import re
import argparse
import os

def parse_did(did_content):
    """
    Parses a DID file and extracts key information for review.
    """
    data = {
        "summary": "Unknown",
        "type": "Unknown",
        "impacts": [],
        "actions": [],
        "status": "Unknown"
    }
    
    lines = did_content.splitlines()
    for line in lines:
        if line.startswith("**Change Summary**:"):
            data["summary"] = line.replace("**Change Summary**:", "").strip()
        elif line.startswith("**Change Type**:"):
            data["type"] = line.replace("**Change Type**:", "").strip()
        elif line.startswith("**Status**:"):
            data["status"] = line.replace("**Status**:", "").strip()
        
        # Simple extraction for lists
        if line.strip().startswith("*   **Potentially Impacted Documents**"):
            pass # Just a header
        if "impacts" in locals() and line.strip().startswith("*   `"): # Heuristic for lists
             pass

    # A more robust parse would be needed for complex logic, but we keep it simple and display raw for review
    return data

def assist_resolution(did_file):
    if not os.path.exists(did_file):
        print(f"Error: DID file '{did_file}' not found.")
        sys.exit(1)

    print(f"--- DID ASSISTANCE: {os.path.basename(did_file)} ---")
    
    with open(did_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Readout
    print("\n[CONTENT READOUT]")
    # Parse basic metadata
    status_match = re.search(r'\*\*Status\*\*:\s*(.*)', content)
    status = status_match.group(1) if status_match else "Unknown"
    
    if status.lower() not in ['draft', 'rejected']:
        print(f"Notice: This DID is already marked as '{status}'. Assistance is typically for Drafts.")

    print(content)
    print("\n---------------------------------------------------")
    
    # 2. Evidence Sources (Placeholder)
    # In a real tool, this might look up the original diff if linked.
    print("\n[EVIDENCE]")
    print("*   Source Diff: (Not explicitly linked in DID format yet)")
    print("*   To verify, run: git log --stat (check recent commits)")

    # 3. Human Checklist
    print("\n[HUMAN REVIEW CHECKLIST]")
    print(f"1.  Is the Summary accurate? ('{re.search(r'Change Summary\*\*:\s*(.*)', content).group(1) if re.search(r'Change Summary\*\*:\s*(.*)', content) else 'Unknown'}')")
    print("2.  Have you manually checked all listed 'Potentially Impacted Documents'?")
    print("3.  Does this change require an entry in `decisions.md` (Epistemic Change)?")
    print("4.  Are all 'Required Actions' checked off or completed in reality?")

    # 4. Open Questions
    print("\n[JUDGMENT CALLS]")
    print("*   If this DID is 'Editorial' only, you may Dismiss it.")
    print("*   If this DID changed Invariants, verify `architectural_invariants.md`.")

    print("\n[NEXT STEPS]")
    print("To RESOLVE:")
    print(f"    1. Edit {did_file}")
    print("    2. Change '**Status**: Draft' to '**Status**: Applied'")
    print("    3. Commit the DID along with the documentation updates.")

def main():
    parser = argparse.ArgumentParser(description="Human-Assisted DID Resolution Helper")
    parser.add_argument('did_file', help='Path to the DID markdown file')
    
    args = parser.parse_args()
    
    assist_resolution(args.did_file)

if __name__ == "__main__":
    main()
