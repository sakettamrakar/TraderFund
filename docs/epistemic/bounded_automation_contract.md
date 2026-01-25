# Bounded Automation Contract
**Status**: Authoritative.

## 1. Core Principle: Suggestion != Action

Phase 6 introduces **Passive Automation**. This means the system can observe, analyze, and *suggest* actions, but it is strictly forbidden from *taking* those actions autonomously.

## 2. The "Passive Monitor" Constraints

Any skill designated as a "Monitor" (e.g., `Monitor Trigger`) must adhere to the following strict bounds:

1.  **Read-Only**: Monitors may only READ from the filesystem (events, logs, artifacts). They must NEVER write to business data paths (except their own logs).
2.  **No Side Effects**: Monitors must not mute alerts, delete files, or trigger external API calls.
3.  **Suggestion Logging**: The only valid output of a monitor is a **Log Entry** (Level: INFO/WARN) clearly marked as a `SUGGESTION`.
    *   *Correct*: `[SUGGESTION] Found 5 events. Recommended: run_narrative.py`
    *   *Forbidden*: `[ACTION] Found 5 events. Executing run_narrative.py...`
4.  **Idempotency**: Running a monitor 100 times in a row must have the exact same system state as running it once (stateless).

## 3. Escalation Protocol

If a Monitor detects a critical failure state (e.g., drift, stalling):
1.  It logs a high-priority suggestion.
2.  It relies on the human operator (checking logs via `Audit Log Viewer`) to see and act on it.

## 4. Graduation Criteria

A "Passive Monitor" can only graduate to an "Active Automator" (Phase 7+) if:
1.  It has run in Passive Mode for >1 week with 100% suggestion accuracy.
2.  A specific `Decision Ledger` entry authorizes the upgrade.
3.  The `bounded_automation_contract.md` is updated to allow the specific exception.
