# Obligation Index

**Authority**: Governance Plane
**Status**: ACTIVE
**Purpose**: Central tracking of system invariants and architectural obligations.

---

## Architectural Obligations (ARCH)

| ID | Name | Description | Status | Source |
| :--- | :--- | :--- | :--- | :--- |
| `OBL-ARCH-LEGIBILITY` | **Legibility Precedes Power** | No capability shall be added until the system structure is legible and documented. | ✅ ACTIVE | `DWBS_SYSTEM_LANDSCAPE.md` |
| `OBL-ARCH-NO-FLOATING-DOCS` | **No Floating Documentation** | All documentation must be anchored in the System Landscape or Audit. | ✅ ACTIVE | `DWBS_SYSTEM_LANDSCAPE.md` |
| `OBL-NO-IMPLICIT-DECISIONS` | **No Implicit Decisions** | Any artifact that ranks or selects symbols must be declared as Intelligence. | ✅ ACTIVE | `DWBS_DECISION_ADJACENCY_AUDIT.md` |
| `OBL-DECISION-SEMANTIC-CLARITY` | **Decision Semantic Clarity** | Decisions must be distinguished from Research verdicts. | ✅ ACTIVE | `DWBS_DECISION_ADJACENCY_AUDIT.md` |
| `OBL-ARCH-INTELLIGENCE-BOUNDS` | **Intelligence Bounds** | No component may suggest action unless it belongs to the Intelligence Layer and is explicitly marked “Non-Executing”. | ✅ ACTIVE | `DWBS_DECISION_ADJACENCY_AUDIT.md` |
| `OBL-INTELLIGENCE-NON-EXECUTING` | **Non-Executing Intelligence** | Intelligence components must never execute trades. | ✅ ACTIVE | `DWBS_INTELLIGENCE_LAYER.md` |
| `OBL-INTELLIGENCE-RESEARCH-RESPECT` | **Research Respect** | Intelligence must verify research state before suggesting attention. | ✅ ACTIVE | `DWBS_INTELLIGENCE_LAYER.md` |
| `OBL-MARKET-PARITY` | **Market Parity** | Research structures must be identical across markets. | ✅ ACTIVE | `DWBS_INDIA_RESEARCH_INSTANTIATION.md` |
| `OBL-NO-MARKET-SPECIFIC-LOGIC` | **No Market Logic** | Logic resides in Core, not Adapters. Adapters only provide inputs. | ✅ ACTIVE | `DWBS_INDIA_RESEARCH_INSTANTIATION.md` |

---

## Other Obligations (Inferred)

*This section captures obligations referenced in impact assessments and code. It requires full population.*

- `OBL-RG-DEPTH` (Regime Depth)
- `OBL-RG-ALIGNMENT` (Regime Alignment)
- `OBL-RG-VIABILITY` (Regime Viability)
- `OBL-SS-KILLSWITCH` (Safety Killswitch)
- `OBL-SS-CIRCUIT` (Circuit Breaker)
- `OBL-OP-HARNESS` (Orchestration Harness)
- `OBL-CP-BELIEF` (Control Plane Belief)
- `OBL-CP-POLICY` (Control Plane Policy)
