# Jules Functional Validation Task Template

Use this template after running `$jules-delegate` dry-run.

```text
Functional validation task for TraderFund.

Module: <module from docs/functional_validation/module_registry.yaml>
Feature slice: <one narrow behavior>
Primary paths:
- <path>
- <path>

Goal:
Validate whether this feature behaves correctly from input to output. This is not a pytest-count or smoke-test task. Focus on real functional evidence: artifact values, generated values, dashboard fields, API payloads, missing-data behavior, and governance constraints.

Expected behavior:
- <business/system expectation>
- <contract or document to follow>

Evidence required:
- Identify the exact input fixture, artifact, API route, or backend loader used.
- Show the expected value or state and how it is derived.
- Show the actual value or state.
- Report PASS, FAIL, BLOCKED, or NEEDS_FIXTURE.
- If changing code, keep the change narrow and add only the functional validation needed for this slice.

Hard limits:
- Do not use secrets, .env files, broker credentials, or customer data.
- Do not modify capital, execution, or live-trading behavior.
- Do not do broad architecture refactors.
- Do not make dashboard cosmetic cleanup unless required to prove truthfulness.
- Do not create unrelated tests.

Output expected:
1. Short summary of what was validated.
2. Exact evidence paths/commands/fields.
3. Findings.
4. Minimal patch or recommendation.
```

Example dashboard task:

```text
Functional validation task for TraderFund.

Module: dashboard_frontend
Feature slice: one regime dashboard widget from backend response to rendered UI.
Primary paths:
- src/dashboard/backend/loaders
- src/dashboard/frontend/src
- docs/dashboard/dashboard_truth_contract.md

Goal:
Prove whether the widget displays real backend values, not placeholders or silently defaulted garbage. Validate missing-data and stale-data behavior.

Expected behavior:
- Widget value exactly matches backend response.
- Provenance or trace information is visible or available.
- Missing/stale data renders a warning or error state.
- No buy/sell language, arbitrary score, ranking, or misleading directional color.

Output expected:
1. Widget checked.
2. Backend route/loader and response fields.
3. Rendered UI mapping.
4. PASS/FAIL/BLOCKED with evidence.
5. Minimal fix or fixture-backed validation if needed.
```
