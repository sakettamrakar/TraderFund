# Phase 3: Research & Intelligence Validation

**Target Layer**: L1 (Regime), L2 (Narrative), L6 (Discovery)
**Obligation Focus**: `OBL-REGIME-GATE-EXPLICIT`, `INV-NO-SELF-ACTIVATION`

## 3.1 Explicit Regime Gating

Ensure that the Regime Engine is functioning as a hard logic gate for all subsequent research operations.

- [ ] **Task 3.1.1 (Healthy Pipeline)**: Run the Regime Engine on Phase 2 data to output `RegimeState`. Pass this state to the Factor Lens. Validate successful generation of candidates.
- [ ] **Task 3.1.2 (Missing State)**: Block the `RegimeState` artifact. Trigger the Factor Lens or Meta Engine.
- [ ] **Task 3.1.3 (Gate Enforcement)**: Assert that downstream research components throw an explicitly typed `RegimeContextMissingError` and instantly halt. No silent default behavior (e.g., assuming "Neutral") is permitted.

## 3.2 Candidate Determinism (No Output Mutation)

Validate that the intelligence layers produce identical outputs when evaluated against the identical truth epoch.

- [ ] **Task 3.2.1**: Fire the Strategy Lenses against the TE-2026-01-30 data frame. Save the `OpportunityCandidate` pool output list.
- [ ] **Task 3.2.2**: Re-initialize the intelligence module cleanly and repeat.
- [ ] **Task 3.2.3**: Compare the lists. Assert exact equivalence in symbols, scores, source tags, and timestamps.

## 3.3 No Self-Activation Validation

Prove that intelligence generation remains strictly within the theoretical boundaries of the system and has no operational capacity to request its own execution sequences.

- [ ] **Task 3.3.1**: Scan the resulting intelligence payloads for any fields or flags representing "order_type", "buy_command", or "execution_router".
- [ ] **Task 3.3.2**: Assert these fields do not exist (`INV-NO-SELF-ACTIVATION`, `INV-NO-EXECUTION`). The output must strictly be a research candidate, completely devoid of execution intent.
