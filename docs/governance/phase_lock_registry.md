# Phase Lock Registry

## 1. Overview
The **Phase Lock Registry** tracks documents and subsystems that are structurally frozen to preserve system integrity during mutation phases.
Violating a Phase Lock requires a new Governance Envelope (AG_ROUTING).

---

## 2. Locked Contracts (Epistemic Foundation)

| Artifact ID | Artifact Name | Owner | Expiration | Exception Policy |
| :--- | :--- | :--- | :--- | :--- |
| **CON-001** | `market_proxy_sets.md` | Governance | Indefinite | Requires `SYSTEM_MUTATION` |
| **CON-002** | `proxy_dependency_contracts.md` | Architecture | Indefinite | Requires `SYSTEM_MUTATION` |
| **CON-003** | `truth_epoch_scoping.md` | Epistemic | Indefinite | **NEVER** |

## 3. Mutable Registries (Operational State)

| Artifact ID | Registry Name | Owner | Mutability | Trigger |
| :--- | :--- | :--- | :--- | :--- |
| **REG-001** | `coverage_gap_register.md` | Data | **Open** | Discovery of new Gap |
| **REG-002** | `data_source_governance.md`| Data | **Open** | New Ingestion Source |
| **REG-003** | `degraded_state_registry.md`| Logic | **Open** | Detection of Failure Mode |

---

## 4. Audit Trail
*   **2026-01-30**: Initial Lock established post-DRY_RUN of Proxy Ignition.
