---
name: change-summarizer
description: Drafts a human-readable summary of provided diffs and a draft Documentation Impact Declaration (DID).
---

# Change Summarizer Skill

**Status:** Operational  
**Skill Category:** Meta (Informational)

## 1. Skill Purpose
The `change-summarizer` synthesizes complex code/config changes (diffs) into high-level, intent-focused narratives. It bridges the gap between mechanical changes and architectural "Why."

## 2. Invocation Contract

### Standard Grammar
```
Invoke change-summarizer
Mode: <DRY_RUN | REAL_RUN>
Target: <git_diff_range | commit_hash | diff_file>
ExecutionScope:
  mode: all
Options:
  draft-did: <enabled | disabled>
  context: <project_intent | architectural_invariants>
```

## 3. Supported Modes & Selectors
- **DRY_RUN**: Generate the summary to stdout only.
- **REAL_RUN**: Generate the summary AND create a `Draft` DID in `docs/impact/` if `draft-did` is enabled.

## 4. Hook & Skill Chaining
- **Chained From**: Invoked after code changes are detected or as a manual analysis step.
- **Chained To**: Produces DIDs that must be resolved by **Humans**.

## 5. Metadata & State
- **Inputs**: Diffs, `project_intent.md`, `active_constraints.md`.
- **Outputs**: Plain-language summary, `.md` Draft DID.

## 6. Invariants & Prohibitions
1.  **Zero Authority**: CANNOT decide if a change is correct or safe.
2.  **No Justification**: CANNOT justify a violation of Project Intent.
3.  **No Auto-Resolution**: CANNOT mark a DID as `Applied` or `Resolved`.
4.  **No Mutation**: NEVER modifies source code or authoritative ledgers.

## 7. Example Invocation
```
Invoke change-summarizer
Mode: REAL_RUN
Target: "HEAD~1..HEAD"
ExecutionScope:
  mode: all
Options:
  draft-did: enabled
```
