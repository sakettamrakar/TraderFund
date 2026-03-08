# Phase 5: Dashboard Integrity Validation

**Target Layer**: Dashboard UI & Data Projection Interfaces
**Obligation Focus**: `INV-READ-ONLY-DASHBOARD`, `OBL-DATA-PROVENANCE-VISIBLE`

## 5.1 Immutable Observer Mode Check

Validate that the Dashboard acts exclusively as a one-way mirror, incapable of mutating backend states.

- [ ] **Task 5.1.1**: Scan the dashboard API connector configurations.
- [ ] **Task 5.1.2**: Assert that ONLY `GET` requests are enabled. Any `POST`, `PUT`, or `DELETE` methods attached to system cognitive layers must trigger a strict linting and runtime failure (`INV-READ-ONLY-DASHBOARD`).
- [ ] **Task 5.1.3**: Verify that all interactive UI toggles act strictly on local view states, not canonical memory variables.

## 5.2 Provenance Binding Check

Ensure that every piece of actionable intelligence presented on the dashboard carries an undeniable link to its foundational data source.

- [ ] **Task 5.2.1**: Programmatically sample JSON Payloads bound for the Dashboard components (e.g., `HighConvictionIdeas`, `RegimeState`).
- [ ] **Task 5.2.2**: Assert the presence of the `source_artifact`, `trace_id`, and `epoch_bounded` fields in the payload (`OBL-DATA-PROVENANCE-VISIBLE`).
- [ ] **Task 5.2.3**: Test the UI renderer structure to assert that these fields are legally required for a successful widget render, throwing a blank 'UNAVAILABLE' visual state if the provenance fields are missing.

## 5.3 Honest Degradation Visualization

Verify that stale logic or lagging indices are actively declared in the UI, rather than hidden by last-known-values.

- [ ] **Task 5.3.1**: Inject a known stale `RegimeState` (e.g., date-stamp is T-3) into the dashboard data-feed.
- [ ] **Task 5.3.2**: Assert that the UI payload renderer overrides the default view with the "STALE (DO NOT TRUST)" visual schema, as defined in the deep-dive observability metrics contract.
