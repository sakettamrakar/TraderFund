# Skill: Change Summarizer

**Category**: Meta (Informational)  
**Stability**: Core

## 1. Purpose
The `change-summarizer` bridges the gap between low-level code/config changes (diffs) and philosophical "Why." It synthesizes diffs into high-level narratives and drafts Documentation Impact Declarations (DIDs).

## 2. Inputs & Preconditions
- **Required Inputs**: Git diff range, commit hash, or explicit diff file.
- **Required Context**: Access to `project_intent.md` and `active_constraints.md` for alignment.

## 3. Outputs & Side Effects
- **Primary Output**: A plain-language summary of intent, mechanism, and impact.
- **DID Impact**: Creates a `Draft` DID in `docs/impact/` if enabled.
- **Ledger Impact**: NONE.

## 4. Invariants & Prohibitions
- **Zero Authority**: CANNOT decide if a change is correct.
- **No Justification**: CANNOT provide justification for a violation of Project Intent.
- **No Mutation**: NEVER modifies source code or authoritative ledgers.
- **Human Blocker**: All drafted DIDs MUST be reviewed and finalized by a human.

## 5. Invocation Format

```
Invoke change-summarizer
Mode: REAL_RUN
Target: "HEAD~1..HEAD"

Options:
  draft-did: enabled
  context: project_intent
```

## 6. Failure Modes
- **Ambiguous Diffs**: Changes too large or contextually disconnected to summarize (Terminal).
- **Missing Baseline**: Unable to find original state for comparison (Terminal).

## 7. Notes for Operators
- **When to Use**: Trigger after every meaningful PR or configuration update.
- **Standard Process**: The summary generated here should be used as the description for the corresponding `evolution-recorder` log.
