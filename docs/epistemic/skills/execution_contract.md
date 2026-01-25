# Execution Contract

**Status**: Authoritative.

This document defines the interface and constraints for executing cognitive skills within the Trader Fund ecosystem. The "Execution Harness" is the only authorized mechanism for invoking skills.

## 1. Execution Principles

1.  **Explicit Invocation**: Skills are invoked explicitly by name. There is no "auto-pilot" or "general intelligence" mode.
2.  **Explicit Inputs**: All required context (diffs, files, parameters) must be provided explicitly at invocation time by the operator.
3.  **Human Attribution**: Every execution must be directly attributable to a human operator. The "system" does not wake up and decide to run a skill.
4.  **No Auto-Selection**: The harness does NOT decide which skill to run. The operator must know the tool they are reaching for.
5.  **Draft Output**: Skill outputs are treated as **Drafts** (epistemically tentatively) until reviewed and applied by a human.
6.  **No Implied Correctness**: Successful execution of a skill does not imply the output is correct, safe, or approved.

## 2. Execution Rules (Forbidden Actions)

To ensure safety and containment, the following functionalities are **strictly forbidden** in the execution harness:

*   **No Automatic Execution**: No triggers from CI/CD, webhooks, or cron jobs.
*   **No Skill Chaining**: The harness must not allow one skill to output directly into the input of another skill without human middleware.
*   **No Background Runs**: Skills run synchronously in the foreground. "Set and forget" background processing is prohibited.
*   **No Authority Escalation**: The harness cannot elevate the privileges of a skill.
*   **No Intent Inference**: The harness passes inputs blindly; it does not attempt to "guess" what the operator wants.

## 3. The CLI Wrapper

The authorized entry point for skills is the CLI wrapper located at `bin/run-skill`.

### Standard Usage
```bash
python bin/run-skill <skill-name> [flags] <inputs>
```

### Example
```bash
python bin/run-skill change-summarizer --diff-range HEAD~1..HEAD
```

## 4. Operational Logging
Every execution must log the following metadata to stdout or a transient log:
*   **Operator**: (Inferred from environment/user)
*   **Timestamp**: UTC execution time.
*   **Skill**: Name of the skill invoked.
*   **Inputs**: Arguments provided.
