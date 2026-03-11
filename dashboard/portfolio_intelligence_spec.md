# Portfolio Intelligence Dashboard — Component Specification

**Version**: 1.0.0  
**Status**: DESIGN (DRY_RUN)  
**Author**: Governed Execution — ChatGPT → Antigravity  
**Truth Epoch**: `TRUTH_EPOCH_2026-03-06_01` (FROZEN)  
**Scope**: US, INDIA  
**Date**: 2026-03-08

---

## 1. Design Philosophy

The Portfolio Intelligence dashboard module extends the existing TraderFund Market Intelligence Dashboard with a new section dedicated to user portfolio analysis. It follows the same design language, component patterns, and governance principles as the existing dashboard.

### Core Principles

1. **Observer Only** — The dashboard is strictly read-only. No write operations, no execution hooks.
2. **Provenance Visible** — Every panel shows its data source and truth epoch.
3. **Staleness Honest** — Data freshness is never hidden. Stale data is visually degraded.
4. **Severity-Driven** — Colors follow the established severity palette (INFO → CRITICAL).
5. **Market-Scoped** — All components are market-parameterised (US / INDIA / Combined).
6. **Advisory Language** — All insights use observational language, never imperative.

### Design Language (Extending Existing)

The dashboard uses the same dark theme and visual vocabulary as the existing components:

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-primary` | `#0a0a0f` | Panel backgrounds |
| `--bg-secondary` | `#12121a` | Card backgrounds |
| `--bg-elevated` | `#1a1a2e` | Hover/active states |
| `--border-default` | `#2a2a3e` | Panel borders |
| `--text-primary` | `#e4e4e7` | Primary text |
| `--text-secondary` | `#9ca3af` | Secondary text |
| `--text-muted` | `#6b7280` | Labels, provenance |
| `--severity-info` | `#3b82f6` | INFO level |
| `--severity-yellow` | `#f59e0b` | YELLOW level |
| `--severity-orange` | `#f97316` | ORANGE level |
| `--severity-red` | `#ef4444` | RED level |
| `--severity-critical` | `#ec4899` | CRITICAL level |
| `--accent-green` | `#10b981` | Positive PnL, healthy scores |
| `--accent-red` | `#ef4444` | Negative PnL, risk |
| `--accent-blue` | `#3b82f6` | Neutral, informational |

---

## 2. Dashboard Layout

### Integration with Existing Dashboard

The Portfolio Intelligence section is added as a **new navigable tab** in the dashboard, accessible via a top-level tab bar that is inserted below the existing `SystemPosture` component.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TRADERFUND MARKET INTELLIGENCE DASHBOARD                               │
│  [Temporal Truth Banner]                                                │
│  [System Status]                                                        │
│  [System Posture]                                                       │
│  ┌───────────────────┬──────────────────────┐                          │
│  │  MARKET INTEL (●)  │  PORTFOLIO INTEL (○)  │  ← NEW TAB BAR         │
│  └───────────────────┴──────────────────────┘                          │
│                                                                         │
│  ┌─── When "PORTFOLIO INTEL" tab is active ───────────────────────────┐│
│  │                                                                     ││
│  │  [Portfolio Overview Panel]                                         ││
│  │  [Multi-Market Selector: US | INDIA | COMBINED]                    ││
│  │                                                                     ││
│  │  ┌──── Left Column ────────┬──── Right Column ────────────────┐    ││
│  │  │                          │                                  │    ││
│  │  │  Holdings Intelligence  │  Diversification Panel           │    ││
│  │  │  Grid                   │                                  │    ││
│  │  │                          │  Risk Monitor                   │    ││
│  │  │                          │                                  │    ││
│  │  │                          │  Resilience Score Card           │    ││
│  │  │                          │                                  │    ││
│  │  │  Performance Analytics  │  Opportunity & Risk Panel        │    ││
│  │  │                          │                                  │    ││
│  │  │  Strategic Insights     │                                   │    ││
│  │  │  Feed                   │                                   │    ││
│  │  └──────────────────────────┴──────────────────────────────────┘    ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  [Footer: System Posture Disclaimer]                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Portfolio Overview Panel

**Component**: `PortfolioOverview.jsx`  
**API**: `GET /api/portfolio/overview/{market}`  
**Purpose**: Top-level portfolio summary with key metrics.

#### Visual Layout

```
┌─ PORTFOLIO OVERVIEW ─────────────────────────────────────────────────────┐
│                                                                          │
│  ┌──────────────┬──────────────┬──────────────┬──────────────────────┐   │
│  │  TOTAL VALUE  │  TOTAL PnL    │  POSITIONS    │  RESILIENCE SCORE  │   │
│  │  $125,430     │  +$8,290      │  18           │  0.72 ADEQUATE     │   │
│  │               │  (+7.1%)  ▲   │               │  ████████░░        │   │
│  └──────────────┴──────────────┴──────────────┴──────────────────────┘   │
│                                                                          │
│  ┌──── Allocation Breakdown ─────────────────────────────────────────┐   │
│  │  ████████████████████████████████████████████████████████████████  │   │
│  │  Technology 35%  │  Healthcare 20%  │  Finance 15%  │  Other 30%  │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Truth Epoch: TRUTH_EPOCH_2026-03-06_01  │  Data as of: 2026-03-08      │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Props

```typescript
interface PortfolioOverviewProps {
  market: "US" | "INDIA" | "COMBINED";
}
```

#### Data Contract

```json
{
  "portfolios": [
    {
      "portfolio_id": "my_us_portfolio",
      "display_name": "US Core Holdings",
      "market": "US",
      "broker": "SCHWAB",
      "total_value": 125430.00,
      "total_cost_basis": 117140.00,
      "total_pnl": 8290.00,
      "total_pnl_pct": 7.08,
      "holding_count": 18,
      "last_updated": "2026-03-08T12:00:00Z"
    }
  ],
  "aggregated": {
    "total_value": 125430.00,
    "total_pnl": 8290.00,
    "total_pnl_pct": 7.08,
    "total_positions": 18,
    "resilience_score": 0.72,
    "resilience_classification": "ADEQUATE"
  },
  "allocation_breakdown": {
    "Technology": 35.2,
    "Healthcare": 20.1,
    "Financials": 15.3,
    "Consumer Discretionary": 12.8,
    "Other": 16.6
  },
  "truth_epoch": "TRUTH_EPOCH_2026-03-06_01",
  "data_as_of": "2026-03-08T12:00:00Z",
  "trace": {
    "source": "data/portfolio_intelligence/analytics/US/"
  }
}
```

#### Behavior
- PnL value colored green (positive) or red (negative)
- Allocation bar uses distinct colors per sector
- Clicking a portfolio name navigates to holdings detail
- If no portfolios imported: show "No portfolios imported. Upload a broker CSV to begin."

---

### 3.2 Holdings Intelligence Grid

**Component**: `HoldingsIntelligenceGrid.jsx`  
**API**: `GET /api/portfolio/holdings/{market}/{portfolio_id}`  
**Purpose**: Per-stock diagnostics table with intelligence cards.

#### Visual Layout

```
┌─ HOLDINGS INTELLIGENCE ──────────────────────────────────────────────────┐
│  Portfolio: US Core Holdings  │  18 positions  │  Filter: [All ▼]       │
│                                                                          │
│  ┌──────┬─────────┬─────────┬────────┬─────────┬──────────┬──────────┐  │
│  │ SYM  │ WEIGHT  │  PnL    │ CONV.  │ REGIME  │ RISK     │ CLASS    │  │
│  ├──────┼─────────┼─────────┼────────┼─────────┼──────────┼──────────┤  │
│  │ AAPL │  8.2%   │ +12.3%  │  0.82  │   ✅    │          │ CORE_HOLD│  │
│  │ TSLA │  6.1%   │ -4.8%   │  0.45  │   ⚠️    │ ⚠ VOL   │ UNDER_REV│  │
│  │ MSFT │  7.5%   │ +18.1%  │  0.91  │   ✅    │          │ CORE_HOLD│  │
│  │ META │  5.3%   │ +8.4%   │  0.67  │   ✅    │          │ MOMENTUM │  │
│  │ NVDA │  4.8%   │ -2.1%   │  0.38  │   ❌    │ 🔴 FUND │ DETERIOR │  │
│  │ ...  │  ...    │  ...    │  ...   │   ...   │   ...    │  ...     │  │
│  └──────┴─────────┴─────────┴────────┴─────────┴──────────┴──────────┘  │
│                                                                          │
│  ▶ Click row to expand holding intelligence card                         │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Expanded Holding Card (on row click)

```
┌─ AAPL — Apple Inc. ──────────────────────────────────────────────────────┐
│                                                                          │
│  ┌── Fundamentals ──┬── Technical ──────┬── Factor Exp. ──┬── Sent. ──┐ │
│  │                   │                   │                  │           │ │
│  │  PE: 28.4         │  Trend: UP ▲      │  Growth: 0.72   │   News:   │ │
│  │  EPS Growth: 15%  │  Momo:  0.78      │  Value:  0.45   │   NORMAL  │ │
│  │  Revenue: +8.2%   │  Vol:   NORMAL     │  Momentum: 0.81 │           │ │
│  │  Net Margin: 25%  │  Support: $178     │  Quality: 0.88  │  Earnings │ │
│  │  BS Health: 0.89  │  Resist: $195      │  M.Sens: 0.35   │  in 45d   │ │
│  │                   │                   │                  │           │ │
│  │  Score: 0.85 ███  │  Score: 0.78 ███  │  Align: 0.81 ██ │  0.60 ██  │ │
│  └───────────────────┴───────────────────┴──────────────────┴───────────┘ │
│                                                                          │
│  Conviction Score: 0.82 ████████████████░░  │  Class: CORE_HOLD         │
│  Regime: ✅ Compatible (TRENDING regime aligns with momentum holding)    │
│  Risk Flags: None                                                        │
│                                                                          │
│  Source: Alpha Vantage + local compute  │  Staleness: 2.5h               │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Props

```typescript
interface HoldingsIntelligenceGridProps {
  market: "US" | "INDIA";
  portfolioId: string;
}
```

#### Behavior
- Sortable by any column (weight, PnL, conviction, class)
- Filterable by opportunity class and risk flag presence
- Row click expands inline intelligence card
- Conviction score rendered as progress bar with color gradient
- Risk flags use severity chip styling

---

### 3.3 Diversification Panel

**Component**: `DiversificationPanel.jsx`  
**API**: `GET /api/portfolio/diversification/{market}/{portfolio_id}`  
**Purpose**: Visual analysis of sector, factor, and geographic concentration.

#### Visual Layout

```
┌─ DIVERSIFICATION ANALYSIS ───────────────────────────────────────────────┐
│                                                                          │
│  ┌──── Sector Allocation ────────┬──── Factor Exposure ──────────────┐  │
│  │                                │                                   │  │
│  │    Technology  ████████ 35%    │    Growth     ████████ 40%        │  │
│  │    Healthcare  █████   20%    │    Quality    ██████  30%         │  │
│  │    Financials  ████    15%    │    Momentum   ████   20%          │  │
│  │    Cons. Disc  ███     13%    │    Value      ██     10%          │  │
│  │    Other       ████    17%    │                                   │  │
│  │                                │    Factor HHI: 0.30 (TILTED)     │  │
│  │    Sector HHI: 0.18 (MOD.)    │                                   │  │
│  └────────────────────────────────┴───────────────────────────────────┘  │
│                                                                          │
│  ┌──── Geographic Exposure ──────┬──── Concentration Metrics ────────┐  │
│  │                                │                                   │  │
│  │    US:    ████████████ 100%    │    Effective Positions: 12.4      │  │
│  │    India: ░░░░░░░░░░░   0%    │    Top Holding: 8.2% (AAPL)      │  │
│  │                                │    Top 3: 21.8%                   │  │
│  │    Status: SINGLE_MARKET       │    Top 5: 33.9%                   │  │
│  │                                │    Status: WELL_DISTRIBUTED       │  │
│  └────────────────────────────────┴───────────────────────────────────┘  │
│                                                                          │
│  ⓘ Diversification assessment based on HHI concentration index           │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Behavior
- Horizontal bar charts for sector and factor breakdown
- Color-coded concentration status badges
- In COMBINED market view: geo exposure shows US/INDIA split
- HHI thresholds color-coded (< 0.10 green, 0.10–0.25 amber, > 0.25 red)

---

### 3.4 Risk Monitor

**Component**: `RiskMonitor.jsx`  
**API**: `GET /api/portfolio/risk/{market}/{portfolio_id}`  
**Purpose**: Risk diagnostics with severity-based alerting.

#### Visual Layout

```
┌─ RISK DIAGNOSTICS ───────────────────────────────────────────────────────┐
│                                                                          │
│  ┌──── Risk Score Gauge ────────────────────────────────────────────────┐│
│  │                                                                      ││
│  │              0.42                                                    ││
│  │   ████████████████████░░░░░░░░░░░░░░░░░░░░                          ││
│  │   CONSERVATIVE  MODERATE  AGGRESSIVE  SPECULATIVE                   ││
│  │       ▲                                                              ││
│  │   Classification: MODERATE                                           ││
│  └──────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌──── Drawdown ──────┬──── Macro ──────────┬──── Correlation ────────┐ │
│  │                     │                      │                         │ │
│  │  Sensitivity: 0.35  │  Macro β: 0.52       │  Clusters: 3           │ │
│  │  Max Impact: 2.8%   │  Rate: MODERATE      │  Largest: 42%          │ │
│  │  Tail Risk: LOW     │  Inflation: LOW      │  Risk: MODERATE        │ │
│  └─────────────────────┴──────────────────────┴─────────────────────────┘│
│                                                                          │
│  Active Risk Flags:                                                      │
│  ⚠ SECTOR_CONCENTRATION — Technology at 35% (threshold: 30%)            │
│  ⓘ SINGLE_MARKET — No geographic diversification                        │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Behavior
- Risk score rendered as a gradient gauge bar
- Risk classification badge with severity coloring
- Active risk flags listed with severity chip
- Clicking a risk flag shows detail expansion

---

### 3.5 Opportunity & Risk Panel

**Component**: `OpportunityRiskPanel.jsx`  
**API**: `GET /api/portfolio/insights/{market}/{portfolio_id}`  
**Purpose**: Highlight strongest/weakest holdings and concentration alerts.

#### Visual Layout

```
┌─ OPPORTUNITY & RISK MONITOR ─────────────────────────────────────────────┐
│                                                                          │
│  ┌──── Strongest Holdings ─────────┬──── Weakest Holdings ────────────┐ │
│  │                                  │                                  │ │
│  │  1. MSFT  Conv: 0.91  +18.1%    │  1. NVDA  Conv: 0.38  -2.1%     │ │
│  │     CORE_HOLD ✅                 │     DETERIORATING 🔴             │ │
│  │                                  │                                  │ │
│  │  2. AAPL  Conv: 0.82  +12.3%    │  2. TSLA  Conv: 0.45  -4.8%     │ │
│  │     CORE_HOLD ✅                 │     UNDER_REVIEW ⚠️              │ │
│  │                                  │                                  │ │
│  │  3. META  Conv: 0.67  +8.4%     │  3. INTC  Conv: 0.31  -11.2%    │ │
│  │     MOMENTUM_PLAY 🔵             │     EXIT_CANDIDATE 🔴            │ │
│  └──────────────────────────────────┴──────────────────────────────────┘ │
│                                                                          │
│  ┌──── Concentration Alerts ────────────────────────────────────────────┐│
│  │  ⚠ Technology sector at 35.2% — approaching concentration threshold  ││
│  │  ⓘ Top 3 holdings represent 21.8% — within acceptable range         ││
│  │  ⚠ Growth factor dominance at 40% — portfolio is factor-tilted      ││
│  └──────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────┘
```

---

### 3.6 Multi-Market View

**Component**: `MultiMarketView.jsx`  
**API**: `GET /api/portfolio/combined`  
**Purpose**: Cross-market portfolio comparison and combined exposure analysis.

#### Visual Layout

```
┌─ MULTI-MARKET PORTFOLIO VIEW ────────────────────────────────────────────┐
│                                                                          │
│  ┌── India Portfolio ────┬── US Portfolio ──────┬── Combined ──────────┐ │
│  │                        │                      │                      │ │
│  │  Value: ₹8,45,000      │  Value: $125,430     │  Combined: $135,670  │ │
│  │  PnL: +₹42,300 (+5.3%) │  PnL: +$8,290 (+7.1%)│  PnL: +$8,810(+6.9%)│ │
│  │  Positions: 12          │  Positions: 18        │  Total: 30          │ │
│  │  Resilience: 0.68       │  Resilience: 0.72     │  Combined: 0.70     │ │
│  └────────────────────────┴──────────────────────┴──────────────────────┘ │
│                                                                          │
│  ┌──── Combined Sector Exposure ────────────────────────────────────────┐│
│  │  Technology    ████████████ 32%  (US: 35% | IN: 28%)                 ││
│  │  Financials    ████████    22%  (US: 15% | IN: 30%)                  ││
│  │  Healthcare    ██████      18%  (US: 20% | IN: 15%)                  ││
│  │  Other         ████████    28%                                        ││
│  └──────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌──── Cross-Market Insights ───────────────────────────────────────────┐│
│  │  ⓘ Geographic split: US 92.5% | India 7.5% — highly US concentrated  ││
│  │  ⚠ Technology exposure is elevated in BOTH markets                   ││
│  │  ✅ Factor distribution differs — natural cross-market diversification ││
│  └──────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  FX Rate: 1 USD = 83.45 INR (Source: canonical proxy)                    │
│  Truth Epoch: TRUTH_EPOCH_2026-03-06_01                                  │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Behavior
- India values shown in INR, US in USD, combined in USD
- FX conversion rate and source explicitly displayed
- Sector bars show per-market breakdown on hover
- Cross-market insights generated from combined analytics

---

### 3.7 Strategic Insights Feed

**Component**: `StrategicInsightsFeed.jsx`  
**API**: `GET /api/portfolio/insights/{market}/{portfolio_id}`  
**Purpose**: Scrollable feed of analytical insights with severity categorization.

#### Visual Layout

```
┌─ STRATEGIC INSIGHTS ─────────────────────────────────────────────────────┐
│                                                                          │
│  Filter: [All ▼]  [DIVERSIFICATION ○]  [RISK ○]  [REGIME ○]  [FUND ○]  │
│                                                                          │
│  ┌──── 🟠 ORANGE ────────────────────────────────────────────────────┐   │
│  │  FACTOR IMBALANCE                                                  │   │
│  │  Portfolio is significantly tilted toward Growth factor (40%).      │   │
│  │  Quality and Value factors are underrepresented relative to a      │   │
│  │  balanced portfolio.                                                │   │
│  │                                                                    │   │
│  │  Affected: AAPL, MSFT, META, NVDA                                 │   │
│  │  Confidence: 0.85  │  Source: factor_module                        │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──── 🟡 YELLOW ────────────────────────────────────────────────────┐   │
│  │  MACRO VULNERABILITY                                               │   │
│  │  3 holdings show elevated macro sensitivity (β > 0.7) while the    │   │
│  │  current macro regime indicates potential rate tightening.          │   │
│  │                                                                    │   │
│  │  Affected: TSLA, NVDA, SHOP                                       │   │
│  │  Confidence: 0.72  │  Source: risk_diagnostics                     │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──── ℹ️ INFO ──────────────────────────────────────────────────────┐   │
│  │  IMPROVING_MOMENTUM                                                │   │
│  │  2 holdings show positive momentum acceleration over the past      │   │
│  │  10 trading sessions with increasing volume support.               │   │
│  │                                                                    │   │
│  │  Affected: META, AMZN                                              │   │
│  │  Confidence: 0.68  │  Source: technical_module                     │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ⚠ These insights are analytical observations only. They do not         │
│  constitute investment advice or trading recommendations.                │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Behavior
- Insights sorted by severity (RED → ORANGE → YELLOW → INFO)
- Filterable by category
- Each insight card shows affected holdings, confidence, and source
- Mandatory advisory disclaimer footer
- Insight cards use left-border severity coloring

---

### 3.8 Resilience Score Card

**Component**: `ResilienceScoreCard.jsx`  
**API**: `GET /api/portfolio/resilience/{market}/{portfolio_id}`  
**Purpose**: Overall portfolio resilience assessment with dimensional breakdown.

#### Visual Layout

```
┌─ PORTFOLIO RESILIENCE ───────────────────────────────────────────────────┐
│                                                                          │
│  ┌──── Overall Score ───────────────────────────────────────────────────┐│
│  │                                                                      ││
│  │              0.72 — ADEQUATE                                         ││
│  │  ████████████████████████████████████████████████░░░░░░░░░░░░░░░░    ││
│  │  FRAGILE       VULNERABLE       ADEQUATE        ROBUST               ││
│  │                                     ▲                                ││
│  └──────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  ┌──── Component Scores ────────────────────────────────────────────────┐│
│  │                                                                      ││
│  │  Diversification    ████████████░░░░  0.65                           ││
│  │  Risk Management    █████████████░░░  0.72                           ││
│  │  Regime Alignment   ████████████████░  0.85                          ││
│  │  Fundamental Quality ██████████████░░  0.78                          ││
│  │  Momentum Health    ████████████░░░░  0.68                           ││
│  │                                                                      ││
│  │  Weakest Dimension: Diversification (0.65)                           ││
│  │  Strongest Dimension: Regime Alignment (0.85)                        ││
│  └──────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  Computed at: 2026-03-08T12:00:00Z  │  Epoch: TRUTH_EPOCH_2026-03-06_01 │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Behavior
- Overall score gauge with classification bands
- Component scores as horizontal progress bars
- Weakest/strongest dimension called out
- Color gradient: green (> 0.75) → amber (0.50–0.75) → red (< 0.50)

---

## 4. API Service Layer

### File: `src/dashboard/frontend/src/services/portfolioApi.js`

```javascript
const API_BASE = '';  // Relative to proxy

export async function getPortfolioOverview(market) {
  const res = await fetch(`${API_BASE}/api/portfolio/overview/${market}`);
  if (!res.ok) throw new Error(`Portfolio overview fetch failed: ${res.status}`);
  return res.json();
}

export async function getHoldingsIntelligence(market, portfolioId) {
  const res = await fetch(`${API_BASE}/api/portfolio/holdings/${market}/${portfolioId}`);
  if (!res.ok) throw new Error(`Holdings fetch failed: ${res.status}`);
  return res.json();
}

export async function getDiversification(market, portfolioId) {
  const res = await fetch(`${API_BASE}/api/portfolio/diversification/${market}/${portfolioId}`);
  if (!res.ok) throw new Error(`Diversification fetch failed: ${res.status}`);
  return res.json();
}

export async function getRiskDiagnostics(market, portfolioId) {
  const res = await fetch(`${API_BASE}/api/portfolio/risk/${market}/${portfolioId}`);
  if (!res.ok) throw new Error(`Risk fetch failed: ${res.status}`);
  return res.json();
}

export async function getPortfolioStructure(market, portfolioId) {
  const res = await fetch(`${API_BASE}/api/portfolio/structure/${market}/${portfolioId}`);
  if (!res.ok) throw new Error(`Structure fetch failed: ${res.status}`);
  return res.json();
}

export async function getPerformanceAnalytics(market, portfolioId) {
  const res = await fetch(`${API_BASE}/api/portfolio/performance/${market}/${portfolioId}`);
  if (!res.ok) throw new Error(`Performance fetch failed: ${res.status}`);
  return res.json();
}

export async function getStrategicInsights(market, portfolioId) {
  const res = await fetch(`${API_BASE}/api/portfolio/insights/${market}/${portfolioId}`);
  if (!res.ok) throw new Error(`Insights fetch failed: ${res.status}`);
  return res.json();
}

export async function getResilienceScore(market, portfolioId) {
  const res = await fetch(`${API_BASE}/api/portfolio/resilience/${market}/${portfolioId}`);
  if (!res.ok) throw new Error(`Resilience fetch failed: ${res.status}`);
  return res.json();
}

export async function getCombinedPortfolio() {
  const res = await fetch(`${API_BASE}/api/portfolio/combined`);
  if (!res.ok) throw new Error(`Combined portfolio fetch failed: ${res.status}`);
  return res.json();
}
```

---

## 5. State Management

### Portfolio Context

A new React context provides portfolio state across components:

```javascript
// src/dashboard/frontend/src/context/PortfolioContext.jsx

import React, { createContext, useContext, useState, useCallback } from 'react';

const PortfolioContext = createContext({});

export function PortfolioProvider({ children }) {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null);
  const [portfolioView, setPortfolioView] = useState('OVERVIEW'); // OVERVIEW | HOLDINGS | ANALYSIS

  const selectPortfolio = useCallback((id) => {
    setSelectedPortfolioId(id);
    setPortfolioView('HOLDINGS');
  }, []);

  return (
    <PortfolioContext.Provider value={{
      selectedPortfolioId,
      selectPortfolio,
      portfolioView,
      setPortfolioView,
    }}>
      {children}
    </PortfolioContext.Provider>
  );
}

export const usePortfolio = () => useContext(PortfolioContext);
```

---

## 6. Component File Structure

```
src/dashboard/frontend/src/
├── components/
│   ├── portfolio/                        ← NEW: Portfolio Intelligence components
│   │   ├── PortfolioOverview.jsx
│   │   ├── PortfolioOverview.css
│   │   ├── HoldingsIntelligenceGrid.jsx
│   │   ├── HoldingsIntelligenceGrid.css
│   │   ├── DiversificationPanel.jsx
│   │   ├── DiversificationPanel.css
│   │   ├── RiskMonitor.jsx
│   │   ├── RiskMonitor.css
│   │   ├── OpportunityRiskPanel.jsx
│   │   ├── OpportunityRiskPanel.css
│   │   ├── MultiMarketView.jsx
│   │   ├── MultiMarketView.css
│   │   ├── StrategicInsightsFeed.jsx
│   │   ├── StrategicInsightsFeed.css
│   │   ├── ResilienceScoreCard.jsx
│   │   ├── ResilienceScoreCard.css
│   │   ├── PortfolioIntelligenceTab.jsx   ← Tab container
│   │   └── PortfolioIntelligenceTab.css
│   ├── ... (existing components)
├── context/
│   ├── PortfolioContext.jsx               ← NEW
│   ├── InspectionContext.jsx              ← Existing
├── services/
│   ├── portfolioApi.js                    ← NEW
│   ├── api.js                             ← Existing
├── App.jsx                                ← Modified: add tab bar + portfolio tab
└── App.css                                ← Modified: tab bar styles
```

---

## 7. Interaction Patterns

### Tab Navigation

```
MARKET INTEL tab (active by default)  →  Existing dashboard panels
PORTFOLIO INTEL tab                    →  Portfolio Intelligence panels
```

When switching to PORTFOLIO INTEL:
1. The market selector remains active at the top
2. `getPortfolioOverview(market)` is called
3. If portfolios exist: render full portfolio intelligence view
4. If no portfolios: render import prompt

### Holdings Drill-Down Flow

```
Portfolio Overview (click portfolio name)
  → Holdings Intelligence Grid (all holdings)
    → Click row → Expanded Intelligence Card
      → View fundamental, technical, factor, sentiment details
```

### Combined Market Flow

```
Market selector: COMBINED
  → Calls GET /api/portfolio/combined
  → Renders MultiMarketView with cross-market analytics
  → Shows combined sector/factor breakdown
  → Shows cross-market insights
```

---

## 8. Responsive Design

All components follow the existing dashboard responsive breakpoints:

| Breakpoint | Behavior |
|-----------|----------|
| > 1400px | Full two-column layout |
| 1024–1400px | Compressed two-column, smaller charts |
| 768–1024px | Single column, stacked panels |
| < 768px | Mobile: simplified cards, collapsed tables |

The Holdings Intelligence Grid collapses to a card view on mobile, showing only symbol, PnL, and conviction score.

---

## 9. Error States

Every component handles these states:

| State | Display |
|-------|---------|
| Loading | Skeleton placeholder with pulsing animation |
| No Data | "No portfolios imported" message with import guidance |
| API Error | "Unable to load portfolio data" with retry button |
| Stale Data | Amber staleness banner: "Data is X hours old" |
| Partial Data | Individual metric shows "N/A" with tooltip explaining gap |

---

## 10. Accessibility

- All interactive elements have unique IDs for testing
- ARIA labels on all severity indicators
- Color is never the sole indicator — text labels accompany all severity chips
- Tab navigation through all panels and grid rows
- Screen reader announcements for severity levels

---

*This document is a design artifact produced under governed execution mode (DRY_RUN). No dashboard components have been implemented.*
