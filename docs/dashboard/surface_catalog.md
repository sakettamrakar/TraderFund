# Dashboard Surface Catalog

## 1. Purpose
This catalog enumerates every dashboard surface (panel, card, widget, indicator) and classifies its purpose, data source, and governance constraints.

---

## 2. Surface Classification

### 2.1. Observational Surfaces (Read-Only Truth)
These surfaces display computed truth without interpretation or recommendation.

| Surface ID | Name | Purpose | Truth Source |
| :--- | :--- | :--- | :--- |
| `SRF-001` | SystemStatus | Overall system health and gate status | Decision Policy |
| `SRF-002` | PolicyStateCard | Current policy permissions and blocks | `decision_policy_{market}.json` |
| `SRF-003` | FragilityStateCard | Stress state and applied constraints | `fragility_context_{market}.json` |
| `SRF-004` | EpistemicHealthCheck | Proxy status and truth epoch | Parity Status |
| `SRF-005` | DataAnchorPanel | Data provenance and staleness | Data Manifest |
| `SRF-006` | RegimeIndicator | Current regime label and confidence | `regime_context_{market}.json` |
| `SRF-007` | FactorSummary | Factor states (Momentum, Vol, Liq, Breadth) | `factor_context_{market}.json` |

### 2.2. Signal Surfaces (Research-Derived)
These surfaces display computed signals that require regime gating.

| Surface ID | Name | Purpose | Truth Source |
| :--- | :--- | :--- | :--- |
| `SRF-010` | IntelligencePanel | Attention signals (not recommendations) | Intelligence Snapshot |
| `SRF-011` | SignalCard | Individual signal detail | Research Layer |
| `SRF-012` | BlockedSignalsList | Signals blocked by research overlay | Research Layer |

### 2.3. Historical Surfaces (Audit Trail)
These surfaces display historical context for learning and validation.

| Surface ID | Name | Purpose | Truth Source |
| :--- | :--- | :--- | :--- |
| `SRF-020` | RegimeTimeline | Historical regime transitions | Regime Archive |
| `SRF-021` | FactorHistory | Factor state evolution | Factor Archive |
| `SRF-022` | PolicyAuditLog | Policy decision history | Audit Logs |

### 2.4. Diagnostic Surfaces (Development/Debug)
These surfaces are for system health monitoring, not trading decisions.

| Surface ID | Name | Purpose | Truth Source |
| :--- | :--- | :--- | :--- |
| `SRF-030` | ParityStatusCard | India parity gaps and readiness | `india_parity_status.json` |
| `SRF-031` | LayerHealthPanel | Layer-by-layer connectivity | System Diagnostics |
| `SRF-032` | StalenessMonitor | Data freshness indicators | All Artifacts |

---

## 3. Prohibited Surfaces (MUST NEVER EXIST)

| Surface ID | Name | Reason for Prohibition |
| :--- | :--- | :--- |
| `SRF-X01` | BuyButton | Execution hook — violates `INV-NO-EXECUTION` |
| `SRF-X02` | SellButton | Execution hook |
| `SRF-X03` | PositionSizer | Capital allocation — violates `INV-NO-CAPITAL` |
| `SRF-X04` | PortfolioView | Implies holdings — violates non-action |
| `SRF-X05` | PnLTracker | Capital implication |
| `SRF-X06` | RecommendationCard | Implied advice — violates observatory principle |
| `SRF-X07` | AutoTradeToggle | Self-activation — violates `INV-NO-SELF-ACTIVATION` |
| `SRF-X08` | AlertSubscription | Notification that implies action urgency |

---

## 4. Surface Hierarchy
```
Dashboard Root
├── Header Bar
│   ├── Market Selector (US / INDIA)
│   └── SystemStatus (SRF-001)
├── Left Panel (Governance)
│   ├── PolicyStateCard (SRF-002)
│   ├── FragilityStateCard (SRF-003)
│   └── EpistemicHealthCheck (SRF-004)
├── Center Panel (Intelligence)
│   ├── IntelligencePanel (SRF-010)
│   └── SignalCards (SRF-011)
├── Right Panel (Context)
│   ├── RegimeIndicator (SRF-006)
│   ├── FactorSummary (SRF-007)
│   └── DataAnchorPanel (SRF-005)
└── Footer
    └── Disclaimer: "Observation Only — No Execution"
```
