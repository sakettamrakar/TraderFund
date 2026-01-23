---
name: change-summarizer
description: Drafts a human-readable summary of provided diffs and a draft Documentation Impact Declaration (DID). This skill has zero authority and is human-triggered only.
---

# Skill: Change Summarizer

**Status**: Operational Specification.

## 1. Skill Purpose
The **Change Summarizer** is a human-triggered cognitive function designed to synthesize complex low-level changes (diffs) into high-level, intent-focused narratives. Its primary goal is to bridge the gap between "what the code did" and "why the architect did it".

**Implementation**: This skill is backed by a deterministic analysis script located at `.agent/skills/change-summarizer/scripts/summarize_diff.py`. behavior is strictly bounded and read-only.

## 2. Invocation Model

### Triggers
*   **Manual Only**: This skill is triggered **exclusively by a human operator**.
*   **No Automation**: No CI/CD pipeline, cron job, or event listener is permitted to trigger this skill automatically.

### Explicit Inputs
The human operator must provide one of the following authoritative contexts:
1.  **Git Diff Range**: `git diff <sha_old>..<sha_new>`
2.  **Commit Hash**: A specific commit ID to analyze.
3.  **Directory Diff**: Explicit path comparison.

### Analysis Script
The human operator may execute the deterministic script to generate the summary:
```bash
python .agent/skills/change-summarizer/scripts/summarize_diff.py <diff-file> [--draft-did]
```

### Resolution Assistance
The human operator may invoke the resolution helper to review a Draft DID:
```bash
python .agent/skills/change-summarizer/scripts/assist_did_resolution.py <did-file>
```

## 3. Explicit Outputs

### Primary Output
*   **Plain-Language Summary**: A concise narrative describing the change in terms of:
    *   **Intent**: What was the goal?
    *   **Mechanism**: How was it achieved?
    *   **Impact**: What else is affected?

### Secondary Output (Drafting)
*   **Draft Documentation Impact Declaration (DID)**:
    *   The skill MAY generate a file at `docs/impact/YYYY-MM-DD__<scope>__<description>.md`.
    *   **Status Lifecycle**: **Draft** → Reviewed → Resolved.
    *   **Status Constraint**: This skill may ONLY create **Status: Draft**. It may not advance or resolve status.
    *   **Content**: It populates the DID template with inferred impacts based on the provided diff.

## 4. Authority Constraints

*   **Zero Authority**: This skill has **ZERO** authority to decide if a change is correct or safe.
*   **No Justification**: It cannot provide justification for a violation of the Project Intent.
*   **No Inference of Intent**: It must describe what it sees; it cannot invent an intent that is not visible in the code or comments.
*   **No Scope Escalation**: It cannot expand the scope of the change; it only summarizes the provided input.
*   **Context-Only Rule**: Epistemic documents are read strictly for terminology alignment. Reading intent or constraints does NOT grant authority to infer intent, validate correctness, or justify changes.
*   **No Prediction**: The skill must not speculate about future behavior, risk, performance, or outcomes beyond what is directly implied by the provided diff.

## 5. Scope

### Read Scope
*   `docs/epistemic/project_intent.md` (For context alignment)
*   `docs/epistemic/active_constraints.md` (For impact detection)
*   `current_phase.md` (For phase compliance)
*   Provided Source Code Diffs (Read-Only)

### Write Scope
*   `docs/impact/*.md` (Draft Status Only)
*   Terminal Output (Stdout) for Summaries

## 6. Forbidden Actions (Non-Goals)

1.  **No Code Mutation**: This skill must **NEVER** modify source code.
2.  **No Ledger Writing**: This skill must **NEVER** write directly to `decisions.md`, `evolution_log.md`, or `assumption_changes.md`.
3.  **No Chaining**: This skill must **NEVER** trigger another skill automatically.
4.  **No Auto-Resolution**: This skill must **NEVER** automatically resolve or close a DID. Only a human can change status from `Draft` to `Applied`.

## 7. Failure Behavior
*   **Explicit Failure Summary**: If the input diff is ambiguous or too large contextually, the skill must emit a failure summary explaining **why** no output was produced.
*   **No Hallucination**: The skill must never hallucinate missing context.
