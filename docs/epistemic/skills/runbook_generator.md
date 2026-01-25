# Skill: Runbook Generator

**Category**: Meta (Documentation)  
**Stability**: Core

## 1. Purpose
The `runbook-generator` ensures that no task remains "Tribal Knowledge." It creates standardized Markdown templates for operational procedures, reducing the cost of documentation and ensuring system growth is always manually reversible/repeatable.

## 2. Inputs & Preconditions
- **Required Inputs**: Runbook name, Target Phase.
- **Required Context**: [documentation_contract.md](file:///c:/GIT/TraderFund/docs/epistemic/documentation_contract.md).

## 3. Outputs & Side Effects
- **Outputs**: New Markdown file in `docs/runbooks/`.
- **DID Impact**: Automatically declares impact on existing Runbook indexes.

## 4. Invariants & Prohibitions
- **Structure Only**: Does NOT automatically write implementation steps; creates only the requirement and skeleton.
- **Human Gated**: The generated output is a `DRAFT` and MUST be reviewed by a human before successful completion.

## 5. Invocation Format

```
Invoke runbook-generator
Mode: REAL_RUN
Target: docs/runbooks/

Options:
  name: "market_hours_init"
  phase: "3"
  template: "standard"
```

## 6. Failure Modes
- **Index Conflict**: Runbook name already exists (Terminal).

## 7. Notes for Operators
- **Mandatory Trigger**: Every new CLI command or structural layer must trigger a runbook generation task.
- **Completeness**: A task that produces code without a corresponding runbook skeleton is non-compliant with the DWBS.
