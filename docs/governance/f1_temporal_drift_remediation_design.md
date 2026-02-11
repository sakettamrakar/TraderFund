# F1 Temporal Drift Remediation Design

## 1. Problem Restatement
F1 is the accumulation of unresolved temporal distance between:
- `RDT` (Raw Data Time)
- `CTT` (Canonical Truth Time)
- `TE` (Truth Epoch / evaluated system time)

For the current governed freeze (`TE-2026-01-30`), IRR evidence shows sustained `CTT > TE` drift (`US +7d`, `INDIA +10d`) rather than bounded, operator-managed backlog states.

Precise definition:
- Temporal drift is the non-negative delta `CTT - TE` measured per market and tracked over time.
- Critical integrity concern is not drift existence alone, but unbounded drift without explicit catch-up governance.

Reference model:
- `RDT` captures incoming world data.
- `CTT` captures validated canonical data.
- `TE` captures explicitly evaluated truth.
- The separation is intentional; remediation must preserve this separation while constraining unmanaged backlog growth.

## 2. Drift Risk Analysis
Why unbounded drift is dangerous:
- Epistemic freshness decay: policies and narratives can remain attached to stale evaluated truth while canonical data advances.
- Operator ambiguity: identical UI surfaces may mix current canonical context with frozen evaluation context.
- Cross-market divergence amplification: independent drift paths (`US`, `INDIA`) increase interpretation mismatch risk.
- Audit fragility: inability to explain what interval is unevaluated reduces post-hoc legibility.

Why immediate truth advancement is unsafe:
- Current evidence includes schema/path instability and partial canonical inconsistency across orchestration routes.
- Advancing `TE` under unresolved drift controls would convert unknown integrity into authoritative truth.
- Advancement without bounded replay/catch-up protocol risks silent omission of unevaluated windows.

## 3. Allowed Remediation Patterns (Design Only)
The following patterns are allowed as design candidates. None are implemented by this document.

### A. Bounded Drift Windows
- Define market-specific maximum tolerated drift (`MAX_DRIFT_DAYS_US`, `MAX_DRIFT_DAYS_INDIA`).
- Encode status bands:
  - `GREEN`: `0 <= drift <= soft_limit`
  - `YELLOW`: `soft_limit < drift <= hard_limit`
  - `RED`: `drift > hard_limit`
- Require explicit operator acknowledgement before any catch-up transition when in `YELLOW`/`RED`.

### B. Chunked Evaluation Epochs
- Introduce chunked catch-up evaluations where `TE` may move only through declared window segments.
- Each chunk must emit:
  - window bounds (`TE_start`, `TE_end`)
  - market scope
  - pass/fail gate evidence
- No chunk can be skipped without explicit rejection record.

### C. Operator-Mediated Catch-Up Evaluation
- Require an operator-approved catch-up intent before running any drift-reduction process.
- Approval payload should include:
  - target market(s)
  - target window(s)
  - expected resulting `TE`
  - abort conditions
- Reject catch-up attempts lacking complete provenance references.

### D. Maximum Allowable Drift Thresholds
- Define non-negotiable hard caps after which system posture is forced to explicit stagnation mode.
- In forced stagnation:
  - no implied freshness wording
  - suppression attribution must indicate drift-driven hold
  - visible drift metrics become mandatory in governance surfaces

## 4. Explicit Constraints
All F1 remediation designs are constrained by:
- No automatic Truth Epoch advancement.
- No silent recomputation of historical windows.
- No execution enablement and no capital side effects.
- No temporal inference from wall-clock `now`; all transitions must be explicit and logged.
- No replacement of `RDT/CTT/TE` separation with a merged time abstraction.

## 5. Open Design Decisions
Undecided items requiring operator/governance choice:
- Threshold policy:
  - fixed day thresholds vs market-volatility-adjusted thresholds.
- Catch-up granularity:
  - daily chunks vs weekly chunks vs event-bounded chunks.
- Approval authority:
  - single-operator vs dual-control requirement for `RED` drift states.
- Failure handling:
  - whether partial chunk failures roll back entire catch-up session or persist successful sub-windows.
- UI disclosure standard:
  - minimum required drift telemetry fields and alert semantics.
- Cross-market coupling:
  - whether advancement can proceed per-market independently when other market drift exceeds hard cap.

## Design Boundary Statement
This document is design-only for `F1`.
- It does not implement remediation.
- It does not modify ingestion/factor/policy logic.
- It does not address implementation plans for `F2`-`F5` beyond dependency acknowledgement.
