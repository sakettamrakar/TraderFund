# Phase 4: Evaluation & Evolution Validation

**Target Layer**: L7 (Convergence), L8-L9 (Constraints & Portfolio)
**Obligation Focus**: `INV-NO-EXECUTION`, `INV-NO-CAPITAL`

## 4.1 Convergence Scoring Integrity

Validate that the convergence engine effectively prioritizes and grades opportunities generated from Phase 3 without modifying the core data representations.

- [ ] **Task 4.1.1**: Run the `Convergence Engine` over the generated multi-lens candidate pool.
- [ ] **Task 4.1.2**: Assert that the candidate schema is preserved, and only external convergence scoring dimensions (e.g., `lens_overlap_count`, `unified_score`) are appended.
- [ ] **Task 4.1.3**: Test the fallback logic: inject a candidate with an unresolved Factor mismatch. Assert the Convergence Engine applies the correct diagnostic penalty but does not physically delete the candidate.

## 4.2 Absolute Capital Disconnection

Ensure that the Portfolio Intelligence and Risk Constraint layers maintain a strictly read-only, diagnostic posture.

- [ ] **Task 4.2.1**: Run `Constraint Engine` against the finalized `Watchlist`.
- [ ] **Task 4.2.2**: Assert the output is a `DiagnosticState` payload containing size-cap and sector limit alerts.
- [ ] **Task 4.2.3**: Search the entire execution trace for calls to external brokerage endpoints or API routes possessing capital mutation access. Assert 0 hits (`INV-NO-CAPITAL`, `INV-NO-EXECUTION`).

## 4.3 Deterministic Replay Simulation

Verify that combining the execution of Phase 3 and Phase 4 yields a reproducible systemic state.

- [ ] **Task 4.3.1**: Clear all downstream layer memory.
- [ ] **Task 4.3.2**: Trigger the master execution sequence (`relay run --phase intelligence-to-portfolio --epoch TE-2026-01-30`).
- [ ] **Task 4.3.3**: Validate the terminal output artifact hashes exactly against a known good signature for that truth epoch data point.
