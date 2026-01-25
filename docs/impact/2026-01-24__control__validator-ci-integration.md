# Documentation Impact Declaration

**Change Summary**: Integrated Epistemic Validator into CI/CD pipeline.
**Change Type**: Infrastructure

## Impact Analysis
*   **Potentially Impacted Documents**: `docs/contracts/epistemic_drift_validator_specification.md`
*   **Impact Nature**: Ensures all future changes are validated against the 13 epistemic rules automatically.

## Required Actions
*   [x] Create `.github/workflows/epistemic_check.yml`
*   [ ] Verify CI run success on next merge.

## Epistemic Impact
*   **Invariants Affected**: None
*   **Constraints Affected**: All 13 Epistemic Rules

**Status**: Applied
