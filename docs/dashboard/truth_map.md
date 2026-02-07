# Dashboard Truth Map

## 1. Purpose
This document maps every dashboard component to its authoritative upstream truth source.
The goal is **complete traceability**: any value displayed on the dashboard must be derivable from a frozen truth artifact.

---

## 2. Truth Layer Hierarchy
```
DATA LAYER (Raw Market Data)
    ↓
RESEARCH LAYER (Computed Signals)
    ↓
FACTOR LAYER (Factor Context)
    ↓
REGIME LAYER (Regime Context)
    ↓
INTELLIGENCE LAYER (Decision Policy, Fragility Policy)
    ↓
DASHBOARD LAYER (Read-Only Projection)
```

---

## 3. Component → Truth Source Mapping

### 3.1. System Status Panel
| Display Element | Truth Source | Artifact Path |
| :--- | :--- | :--- |
| Execution Gate Status | Decision Policy | `docs/intelligence/decision_policy_{market}.json` |
| Gate Reason | Decision Policy | `.policy_decision.reason` |
| Last Tick | Data Manifest | `data/manifest/{market}/last_tick.json` |
| Governance Status | Parity Status | `docs/intelligence/india_parity_status.json` |

### 3.2. Policy State Card
| Display Element | Truth Source | Artifact Path |
| :--- | :--- | :--- |
| Policy State | Decision Policy | `.policy_decision.policy_state` |
| Permissions | Decision Policy | `.policy_decision.permissions` |
| Blocked Actions | Decision Policy | `.policy_decision.blocked_actions` |
| Reason | Decision Policy | `.policy_decision.reason` |
| Epistemic Health | Decision Policy | `.policy_decision.epistemic_health` |

### 3.3. Fragility State Card
| Display Element | Truth Source | Artifact Path |
| :--- | :--- | :--- |
| Stress State | Fragility Context | `docs/intelligence/fragility_context_{market}.json` |
| Constraints Applied | Fragility Context | `.fragility_context.constraints_applied` |
| Final Authorized Intents | Fragility Context | `.fragility_context.final_authorized_intents` |
| Stress Reason | Fragility Context | `.fragility_context.reason` |

### 3.4. Intelligence Panel (Signals)
| Display Element | Truth Source | Artifact Path |
| :--- | :--- | :--- |
| Signal List | Intelligence Snapshot | `docs/intelligence/snapshots/intelligence_{market}_*.json` |
| Signal Overlay Status | Research Layer | `.signals[].overlay.status` |
| Signal Reason | Research Layer | `.signals[].reason` |

### 3.5. Market Snapshot
| Display Element | Truth Source | Artifact Path |
| :--- | :--- | :--- |
| Price Data | Data Layer | `data/regime/raw/{ticker}.csv` |
| Regime Label | Regime Context | `docs/evolution/context/regime_context_{market}.json` |
| Factor States | Factor Context | `docs/evolution/context/factor_context_{market}.json` |

### 3.6. Data Anchor Panel
| Display Element | Truth Source | Artifact Path |
| :--- | :--- | :--- |
| Truth Epoch | Data Anchor | `docs/intelligence/data_anchor_{market}.json` |
| Proxy Status | Parity Status | `docs/intelligence/india_parity_status.json` |
| Provenance | Parity Status | `.proxy_diagnostics.*.provenance` |

---

## 4. Invariant: No Orphan Displays
Every value shown on the dashboard MUST have an entry in this map.
If a display element cannot be traced to a frozen truth artifact, it is a **violation** and must be removed or connected.
