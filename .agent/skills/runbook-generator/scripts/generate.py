import argparse
import os
import datetime

RUNBOOK_DIR = "docs/runbooks"

TEMPLATE = """# Runbook: {title}
**Status**: DRAFT.
**Created**: {date}

## 1. Purpose & Trigger
**Why run this?**: [Explain the goal]
**When to run this?**: [Define the trigger, e.g., "Monthly" or "On Alert"]

## 2. Pre-requisites
*   [ ] Access Level: {user}
*   [ ] Required Data: [List inputs]

## 3. Execution Steps

### Step 1: [Name]
```powershell
# Command here
```

### Step 2: [Name]
```powershell
# Command here
```

## 4. Verification
**Success Criteria**:
*   [ ] Output file X exists.
*   [ ] Logs contain "Success".

## 5. Troubleshooting
*   **Error**: [Condition]
*   **Fix**: [Resolution]
"""

def create_runbook(name: str, user: str):
    filename = name.lower().replace(" ", "_") + ".md"
    filepath = os.path.join(RUNBOOK_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"Error: Runbook {filename} already exists.")
        return

    content = TEMPLATE.format(
        title=name,
        date=datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        user=user
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Created Template: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Runbook Generator")
    parser.add_argument("--name", required=True, help="Runbook Name (e.g. 'Monthly Cleanup')")
    parser.add_argument("--user", default="ActiveUser", help="Author")
    
    args = parser.parse_args()
    create_runbook(args.name, args.user)

if __name__ == "__main__":
    main()
