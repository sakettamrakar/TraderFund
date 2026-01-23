---
name: Runbook Generator
description: Tool to convert implicit operational knowledge into explicit executable runbooks (Template Generator).
version: 1.0.0
---

# Runbook Generator

**Purpose**: To reduce the friction of creating formal documentation. It generates standardized Runbook templates.

## 1. Capabilities

### 1.1. Scaffolding
*   **Action**: Create new markdown file in `docs/runbooks/`.
*   **Inputs**: Runbook Name, Target Phase.
*   **Output**: A file with headers for:
    *   Purpose/Trigger
    *   Pre-requisites (Permissions, Data)
    *   Execution Steps (CLI commands)
    *   Verification (How to know it worked)
    *   Troubleshooting

## 2. Usage

### Command Line
```powershell
python bin/run-skill.py runbook-generator --name "monthly_cleanup" --user documentation_bot
```
