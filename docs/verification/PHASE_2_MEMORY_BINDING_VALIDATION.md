# Phase 2: Memory Binding Validation

**Target Layer**: L0 → Canonical Memory Store
**Obligation Focus**: `OBL-TRUTH-EPOCH-DISCLOSED`, `OBL-HONEST-STAGNATION`

## 2.1 Truth Epoch Disclosure Checks

Validate that data moving from the ingestion pipelines strictly binds itself to the active temporal truth epoch before persistence.

- [ ] **Task 2.1.1**: Inspect the transformed DTOs from Phase 1. Assert that the `TE-2026-01-30` header is unequivocally attached to every record block.
- [ ] **Task 2.1.2**: Attempt to write a DTO missing the `truth_epoch` field into the silver memory layer. Assert that the system violently rejects the write, proving fail-closed memory binding.

## 2.2 Honest Stagnation Test

Validate the system's response to an expected ingestion gap (e.g., a holiday or technical failure in the upstream API). The system must report stagnation honestly, not propagate stale data as fresh.

- [ ] **Task 2.2.1**: Point the ingestion engine to a known market holiday date.
- [ ] **Task 2.2.2**: Verify that the Canonical Store accurately logs a zero-volume marker or skips the day, but the operational metrics emit an explicit `STAGNANT` or `NO_DATA` warning.
- [ ] **Task 2.2.3**: Assert that `forward_fill` algorithms are NOT triggered. (`OBL-HONEST-STAGNATION`).

## 2.3 Idempotency of State Updates

Validate that rewriting the same known memory state does not result in duplicate records or corrupt indexing.

- [ ] **Task 2.3.1**: Write the TE-2026-01-30 canonical payload sequentially 3 times.
- [ ] **Task 2.3.2**: Query the data frame size and row count. Assert the volume matches exactly exactly 1 write instance.
