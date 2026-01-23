---
name: Cognitive Order Validator
description: Structural skill to enforce the cognitive hierarchy (Architecture > Logic > Execution).
version: 1.0.0
---

# Cognitive Order Validator

**Purpose**: To enforce the strict separation of concerns defined in `architectural_invariants.md`. Specifically, ensuring that "Thinking" components do not perform "Acting".

## 1. Capabilities

### 1.1. Import Layer Check
*   **Target**: Python Source files.
*   **Logic**: Verifies that lower-layer modules (e.g., `signals`, `narratives`) do not import upper-layer execution modules (e.g., `execution`, `adapter`).
*   **Constraint**: `from src.execution import ...` forbidden in `src/narratives`.

### 1.2. Direct Execution Check
*   **Target**: Logic files.
*   **Logic**: Scans for "Action" keywords (e.g., `place_order`, `buy`, `sell`) inside "Cognitive" files.
*   **Output**: Error Report.

## 2. Usage

### Command Line
```powershell
python bin/run-skill.py cognitive-order-validator --target src/ --user validator_bot
```
