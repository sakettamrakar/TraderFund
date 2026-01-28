# Architectural Declaration: Decision Semantics Freeze

**Authority**: `ARCH-1.5`
**Status**: ACTIVE
**Date**: 2026-01-30

## 1. Declaration

To ensure the clean evolution of the Intelligence Layer (Ring-3), the following semantics are now constitutionally frozen:

*   **Research = Truth**: Ring-1 components describe the world. They never suggest action.
*   **Intelligence = Suggestion**: Ring-3 components process research to suggest actions. They never execute.
*   **Execution = Forbidden**: No component in this system is authorized to execute live trades.

## 2. Implication

All artifacts identified as "Intelligence" in the Decision-Adjacency Audit (`docs/architecture/decision_adjacency_disposition.md`) must be treated as **suggestions only**. They have zero authority to move capital.

This document closes Step-1.5.
