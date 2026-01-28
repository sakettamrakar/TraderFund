# DWBS: System Landscape & Architecture Freeze

**Status**: ACTIVE
**Type**: Foundational / One-Time
**Plane**: Architecture & Governance
**Affects**: Documentation only
**Risk**: Zero
**Reversibility**: N/A

---

## 1. Purpose & Non-Goals

### Purpose
To produce a structural legibility of the TraderFund system by mapping all existing components into a "Three-Ring Architecture". This serves as an authoritative architectural freeze to ensure no floating documentation or unclear ownership exists before further capability is added.

### Non-Goals
- Refactoring existing code.
- Adding new features or execution paths.
- Implementing India research logic.
- Implementing Intelligence Layer logic.

---

## 2. Three-Ring Architecture Definition

The system is defined by three immutable rings:

### Ring-1: Core Research (Truth Engine)
**Properties**:
- Market-agnostic
- Symbol-free
- Slow-moving
- Explanatory
- Gating allowed
- Frozen semantics

**Examples**: Macro Context, Regime Engine, Factor Context, Strategy Eligibility, Evolution / Watchers, Governance / DIDs.

### Ring-2: Market Research Adapters
**Properties**:
- Market-specific
- Still research-grade
- Proxy-based (indices, volatility)
- No symbol ranking
- No heuristics

**Examples**: US research instantiation, India research instantiation, Data contracts & proxies.

### Ring-3: Intelligence / Decision Support
**Properties**:
- Human-facing
- Symbol-level
- Heuristic allowed
- Noisy allowed
- **NEVER executes**
- **NEVER gates research**

**Examples**: Watchlists, Breakout scanners, Narrative candidates, “Interesting activity” views.

---

## 3. Documentation Canon Rules

1.  **Authority**: `docs/architecture/system_landscape.md` is the single source of truth for component existence and ownership.
2.  **No Floating Docs**: Every documentation file must be linked or classified in the audit.
3.  **Ring-Bound**: New components must declare their Ring and Market in the landscape inventory.
4.  **Legibility First**: "We do not add capability until the system is legible. Legibility precedes power."

---

## 4. Landscape Deliverables

1.  **System Landscape Inventory** (`docs/architecture/system_landscape.md`): The map of what exists.
2.  **Documentation Audit** (`docs/architecture/documentation_audit.md`): The cleanup plan.
3.  **Convergence Map** (`docs/architecture/convergence_map.md`): The bridge between legacy/future and current state.
4.  **Task Graph** (`docs/epistemic/roadmap/task_graph_landscape.md`): The execution tracking for this work.
5.  **Obligation Index Update** (`docs/governance/obligation_index.md`): Tracking architectural obligations.

---

## 5. Task Graph

See `docs/epistemic/roadmap/task_graph_landscape.md` for the detailed execution graph.
Key Nodes:
- ARCH-1.1: Three-Ring Architecture Definition
- ARCH-1.2: System Component Inventory
- ARCH-1.3: Documentation Audit
- ARCH-1.4: Convergence Mapping
- ARCH-1.5: Architecture Freeze Declaration

---

## 6. Completion Criteria

- [ ] New DWBS exists (`docs/architecture/DWBS_SYSTEM_LANDSCAPE.md`).
- [ ] Complete system landscape inventory exists.
- [ ] Documentation audit exists.
- [ ] Convergence map exists.
- [ ] Task graph exists.
- [ ] Obligation index updated.
- [ ] **No code touched.**
