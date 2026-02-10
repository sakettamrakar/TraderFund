# Architecture Decision Records (ADRs)

> [!IMPORTANT]
> **Authoritative Source**: `docs/memory/03_domain/domain_model.md` is CANONICAL.
> This directory contains the immutable record of architectural decisions.

## What is an ADR?

An **Architecture Decision Record (ADR)** is a document that captures an important architectural decision made along with its context and consequences.

We use ADRs to:
*   **Track Decision History**: Understand why the system is built the way it is.
*   **Enforce Immutability**: Once accepted, a decision is law until explicitly superseded.
*   **Prevent Drift**: By documenting the "Why", we prevent accidental regression.

**Format**:
*   **Context**: The problem or tension prompting the decision.
*   **Decision**: The specific choice made.
*   **Rationale**: Why this choice was made over alternatives.
*   **Consequences**: The trade-offs and impacts (positive and negative).

## Index

| ID | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| **ADR-0001** | [Market Pipeline Isolation](ADR-0001.md) | Accepted | 2026-01-01 |
| **ADR-0002** | [Separation of Signal vs Execution](ADR-0002.md) | Accepted | 2026-01-18 |
| **ADR-0003** | [Adoption of Regime-First Cognition](ADR-0003.md) | Accepted | 2026-01-18 |
| **ADR-0004** | [Shadow-Mode Validation](ADR-0004.md) | Accepted | 2026-01-18 |
| **ADR-0005** | [Epistemic Freeze Protocol](ADR-0005.md) | Accepted | 2026-01-24 |
| **ADR-0006** | [Layered Plane Architecture](ADR-0006.md) | Accepted | 2026-01-24 |
| **ADR-0007** | [Immutable Decision Ledger](ADR-0007.md) | Accepted | 2026-01-22 |
| **ADR-0008** | [Forbidden Execution](ADR-0008.md) | Accepted | 2026-01-01 |
| **ADR-0009** | [Factor Context Explanation](ADR-0009.md) | Accepted | 2026-01-26 |
| **ADR-0010** | [Progressive Trust Model](ADR-0010.md) | Accepted | 2026-01-26 |
| **ADR-0011** | [Multi-Human Governance](ADR-0011.md) | Accepted | 2026-01-24 |
| **ADR-0012** | [Zero-Trust Data Ingestion](ADR-0012.md) | Accepted | 2026-01-22 |
| **ADR-0013** | [Local-First Filesystem Storage](ADR-0013.md) | Accepted | 2026-01-01 |
| **ADR-0014** | [Single-Operator Infrastructure](ADR-0014.md) | Accepted | 2026-01-01 |
| **ADR-0015** | [Bounded Automation Contract](ADR-0015.md) | Accepted | 2026-01-24 |
| **ADR-0016** | [Explicit Truth Epoch](ADR-0016.md) | Accepted | 2026-01-20 |

## Status Codes

- **Proposed**: Under discussion.
- **Accepted**: Ratified and implemented.
- **Deprecated**: Superseded by a later decision.
- **Rejected**: Discussed but not adopted.
