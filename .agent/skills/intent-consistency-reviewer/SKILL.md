---
name: Intent Consistency Reviewer
description: Advisory skill to ensure alignment with Project Intent and Trading Philosophy.
version: 1.0.0
---

# Intent Consistency Reviewer

**Purpose**: To verify that changes (code or docs) do not violate the Core Project Intent (e.g., "Glass Box", "Context Before Signal") or introduce explicitly Forbidden patterns (e.g., "Black Box", "HFT").

## 1. Capabilities

### 1.1. Anti-Pattern Scan
*   **Target**: File or Directory.
*   **Logic**: Scans for forbidden keywords/phrases defined in `project_intent.md` (or hardcoded anti-patterns).
*   **Examples**: "Neural Network", "Black Box", "High Frequency", "Arbitrage".
*   **Output**: Warning Report.

### 1.2. Intent Alignment Check
*   **Target**: `project_intent.md` (Self-Check).
*   **Logic**: Verifies the integrity of the intent document itself (simple checksum/presence).

## 2. Usage

### Command Line
```powershell
python bin/run-skill.py intent-consistency-reviewer --target src/new_module.py --user checks_user
```

## 3. Operational Rules
1.  **Advisory**: This skill cannot block execution, only flag warnings.
2.  **Context Aware**: (Future) Should use LLM to understand context, but V1 uses Heuristics.
