---
name: runbook-generator
description: Tool to convert implicit operational knowledge into explicit executable runbooks (Template Generator).
---

# Runbook Generator Skill

**Status:** Operational  
**Skill Category:** Meta (Documentation)

## 1. Skill Purpose
The `runbook-generator` reduces documentation friction by generating standardized templates for operational procedures. It ensures that every new task has a corresponding "How-To" for human operators.

## 2. Invocation Contract

### Standard Grammar
```
Invoke runbook-generator
Mode: <REAL_RUN | DRY_RUN>
Target: docs/runbooks/
ExecutionScope:
  mode: all
Options:
  name: "<runbook_filename>"
  phase: "<target_phase_number>"
  template: "<standard | emergency | setup>"
```

## 3. Supported Modes & Selectors
- **REAL_RUN**: Creates a new `.md` file in the target directory with prepopulated headers.
- **DRY_RUN**: Prints the template content to stdout without creating a file.

## 4. Hook & Skill Chaining
- **Chained From**: Triggered as a **Post-Execution Hook** for `Infrastructure` or `Workflow` tasks.
- **Chained To**: Manual human review.

## 5. Metadata & State
- **Inputs**: Runbook name, phase context, [documentation_contract.md](file:///c:/GIT/TraderFund/docs/epistemic/documentation_contract.md).
- **Outputs**: New Markdown runbook template.

## 6. Invariants & Prohibitions
1.  **Skeleton Only**: Does NOT automatically write the steps; generates the structural requirement only.
2.  **Alignment**: Must follow the headings defined in the system's documentation standard.
3.  **No Auto-Execution**: Generated runbooks MUST be reviewed by a human before being marked as `SUCCESS` in the task graph.

## 7. Example Invocation
```
Invoke runbook-generator
Mode: REAL_RUN
Target: docs/runbooks/
ExecutionScope:
  mode: all
Options:
  name: "market_hours_init"
  phase: "3"
  template: "standard"
```
