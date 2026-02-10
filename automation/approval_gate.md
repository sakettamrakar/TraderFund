# Approval Gate Policy

## Authority Model

| Layer | Authority | Description |
| :--- | :--- | :--- |
| **Domain Model** (`docs/memory/03_domain`) | **HUMAN ONLY** | The "What" and "Why". Agents may read but never write. |
| **Vision** (`docs/memory/01_vision`) | **HUMAN ONLY** | Long-term strategic direction. |
| **Success Criteria** (`docs/memory/02_success`) | **HUMAN ONLY** | The definition of "Done" and "Safe". |
| **Component Specs** (`docs/memory/05_components`) | **HUMAN MAIN** | Agents may propose drafts (SpecAgent), but humans must approve/merge. |
| **Implementation** (`src/`) | **AGENT** | Agents generate code. Humans review only on exception or audit. |
| **Tests** (`tests/`) | **AGENT** | Agents generate and maintain verification implementations. |
| **Orchestration** (`src/orchestration`) | **AGENT** | Agents wire components based on `pipeline_graph.yaml`. |

## Gating Rules

### 1. Auto-Merge Criteria
Changes are automatically merged if **ALL** of the following are true:
- Source change is limited to `src/` or `tests/`.
- `ValidationAgent` reports **PASS** on all Success Criteria.
- `Shadow Mode` constraints are respected (no leaked side effects).
- No `Governance` layer code is modified.

### 2. Human Approval Required
Execution pauses for human review if **ANY** of the following are true:
- Modification to `Reasoning` or `Governance` layer components.
- Modification to `docs/memory/03_domain/domain_model.md`.
- `ValidationAgent` reports failure loop > 3 attempts.
- Deletion of persistent state or data.
- "High Impact" flag detected in `spec_diff.json`.

### 3. Escalation Protocol
- **Level 1 (Warn)**: Validation failure. Agent retries with self-correction.
- **Level 2 (Pause)**: Repeat failure or Governance touch. Human notified.
- **Level 3 (Lockdown)**: Use of forbidden tool or violation of Invariant. System locks file artifacts and awaits Admin reset.

## Governance Override
Humans retain the right to `VETO` any agent action at any time. A Veto triggers an immediate Rollback to the last known good state (`HEAD@{1}`).
