# Functional Validation Program

## Purpose

This program validates whether TraderFund features behave correctly at the user-visible and system-contract level. It is not a replacement for pytest, smoke tests, or syntax checks.

Functional validation asks questions like:

- Did ingestion produce canonical, fresh, traceable data?
- Did a generated value come from the correct source and formula?
- Did the dashboard populate from real backend artifacts instead of placeholders?
- Did a missing or stale artifact become an explicit warning instead of garbage UI?
- Did the module respect governance rules such as read-only dashboard behavior and no execution/capital mutation?

## Operating Model

1. Identify the module from `module_registry.yaml`.
2. Pick one narrow feature or user-visible behavior inside that module.
3. Run local validation or review existing artifacts when possible.
4. Delegate only small, isolated validation work to Jules using `$jules-delegate`.
5. Require Jules output to include evidence, not just "tests pass".
6. Store results as module-level findings before sending the next Jules task.

## Jules Delegation Rules

Use Jules for one small functional slice at a time. Good Jules tasks include:

- Add or improve one functional validation for a module.
- Trace one dashboard widget from frontend display to backend artifact.
- Verify one generated value against source inputs and formula.
- Add a fixture-backed regression for one known garbage-dashboard case.
- Document one broken feature path with exact evidence and proposed fix.

Do not use Jules for:

- broad architecture redesign
- work requiring local uncommitted changes
- secrets, `.env` files, broker credentials, or customer data
- live trading, execution, or capital-modifying flows
- vague prompts like "test the dashboard"

Before sending a Jules task, run the jules-delegate dry-run and confirm the repo, branch, source, and payload.

## Functional Evidence Standard

Each module validation result must answer:

- Scope: Which module, feature, files, and artifacts were checked?
- Input: Which fixture, canonical artifact, or data source was used?
- Expected behavior: What should happen in business terms?
- Actual behavior: What happened?
- Evidence: Exact command, route, artifact path, rendered widget, JSON field, or calculated value.
- Verdict: PASS, FAIL, BLOCKED, or NEEDS_FIXTURE.
- Next action: Fix, add fixture, improve dashboard binding, or document as intentionally unsupported.

## Dashboard Standard

Dashboard validation must follow `docs/dashboard/dashboard_truth_contract.md`.

A dashboard task is not complete unless it proves:

- the widget is bound to a backend source
- missing data is visible as a warning or error state
- stale data is visible as stale
- displayed values match backend artifacts
- no widget invents scores, rankings, recommendations, or directional cues
- the dashboard remains read-only

## Result Storage

Use `docs/functional_validation/module_registry.yaml` as the queue and ownership map.

For completed investigations, add short run notes under:

```text
docs/functional_validation/runs/
```

Name run notes with:

```text
YYYY-MM-DD_<module>_<feature>.md
```

Keep each run note short and evidence-first.
