# TraderFund Current Repository Assessment

**Assessment date:** 2026-05-17  
**Purpose:** create a single restart document that explains the current repository state, the visible gaps, the unfinished wiring, and the recommended order of work before further implementation.

---

## 1. Executive readout

TraderFund is not one small application anymore. It is a mixed research platform containing ingestion, market intelligence, regime/narrative governance, portfolio intelligence, paper-trading research modules, dashboards, validation tooling, automation agents, and many historical documents/artifacts. The repository has strong conceptual coverage, but the current working state is fragmented.

The biggest issue is not the absence of ideas. The biggest issue is that several partially complete systems coexist without one operational spine:

1. **The README describes a disciplined ingestion → processing → momentum → observation → replay → dashboard workflow, but several referenced commands and paths do not line up cleanly with the repository inventory.**
2. **The documentation layer is rich but divergent.** There are multiple architecture/backlog/status documents with overlapping scopes and different dates, so it is unclear which document is authoritative for day-to-day execution.
3. **Validation exists, but the validation stack itself currently reports missing runtime artifacts and environmental skips.** A direct ingestion validation run failed because canonical raw/processed/US data artifacts were not found, while timestamp/null checks were skipped because `pandas` is unavailable in the current Python environment.
4. **The general pytest suite is not currently a reliable health signal.** Test collection stops with many import-time errors caused by missing dependencies, phase locks, and stale/deleted test surfaces.
5. **The dashboard has both an older static dashboard folder and a newer Vite/React dashboard under `src/dashboard/frontend`, plus a FastAPI backend under `src/dashboard/backend`.** The intended dashboard authority should be clarified.
6. **There are many generated/runtime/data artifacts in the repository tree.** Some are useful evidence, but they make it hard to distinguish source-of-truth code from historical output.

**Recommended next move:** stabilize the repository before adding features. Treat the next phase as a repository reset and wiring phase: choose the canonical architecture, fix environment/test collection, confirm data artifact expectations, define one daily pipeline entry point, then wire dashboard loaders and reports to that pipeline.

---

## 2. Evidence gathered in this assessment

Commands run from the repository root (`/workspace/TraderFund`):

| Command | Result | What it tells us |
| --- | --- | --- |
| `find .. -name AGENTS.md -print` | No files found | No local agent instruction files were present. |
| `git status --short` | Clean before edits | There were no user changes to preserve at assessment start. |
| `rg --files -g '!node_modules' -g '!vendor' -g '!dist' -g '!build' -g '!coverage'` | Large multi-domain source tree | The repo spans Python, React, docs, data, automation, and runtime artifacts. |
| `find . -maxdepth 3 -type d` | Many top-level products/modules | There are overlapping product slices: `src`, `traderfund`, `research_modules`, `automation`, `dashboard`, `docs`, `ingestion`, `paper_trading`, etc. |
| Python inventory script over non-ignored files | 1,795 files found | High repo surface area; top counts were `docs` 604, `src` 249, `automation` 238, `research_modules` 120, `_delete` 115. |
| `python -m pytest --collect-only -q` | Failed with 57 collection errors after collecting 48 tests | Test suite collection is currently blocked by missing deps, phase locks, and stale test locations. |
| `python -m traderfund.validation.validation_runner --phase ingestion --hook audit --market US` | Failed | Validation framework runs, but ingestion schema validation failed due to missing canonical artifacts; timestamp/null checks skipped because pandas is unavailable. |

---

## 3. Current repository shape

### 3.1 Major code surfaces

| Area | Main paths | Current interpretation |
| --- | --- | --- |
| Core application layers | `src/layers`, `src/intelligence`, `src/evolution`, `src/dashboard`, `src/portfolio_intelligence` | Newer platform spine for intelligence, evaluation, portfolio, and dashboard surfaces. |
| Market ingestion and processing | `ingestion`, `processing`, `src/ingestion`, `data_pipeline` | Mixed legacy/new ingestion surfaces for India/US, raw/processed data, schema, and loaders. |
| Research modules | `research_modules/*` | Staged research capabilities including hygiene, capability, energy, participation, momentum, sustainability, backtesting, risk, sentiment, and volatility modules. Some are phase-locked. |
| Regime/narrative package | `traderfund/regime`, `traderfund/narrative`, `narratives` | Regime engine, narrative adapter, genesis, enforcement tests, and market-story integration surfaces. |
| Dashboard | `src/dashboard/backend`, `src/dashboard/frontend`, `dashboard` | There is a newer API + React dashboard and an older static dashboard surface. The canonical dashboard should be declared. |
| Automation and agents | `automation`, `.agent/skills`, `bin` | Autonomous loop, Jules/Gemini executors, semantic/visual quality checks, task routing, local desk skills. |
| Paper trading | `paper_trading/execution`, `paper_trading/analytics` | Research-only/paper phase modules guarded by phase locks. |
| Infra hardening | `infra_hardening` | Alerts, drift detection, scheduler wrapper, validation integrity, and control switches. |
| Documentation/evidence | `docs`, `analysis`, `artifacts`, `logs`, `analytics`, `_delete` | Extensive design, audits, memory, verification, and historical output. Needs source-of-truth cleanup. |

### 3.2 Technology stack currently implied

- **Backend/runtime:** Python modules and scripts.
- **Validation/testing:** `pytest`, bespoke `traderfund.validation` framework, CI epistemic guardrail workflow.
- **Data:** JSON/JSONL, Parquet, SQLite artifact (`nse_data.db`), possible PostgreSQL/InfluxDB references in architecture docs.
- **Frontend:** React 19 + Vite 7 under `src/dashboard/frontend`.
- **External/broker/data integrations:** Alpha Vantage, Angel One SmartAPI, Zerodha/Kite references, Trader News adapter, possible MCP broker connectors.
- **Governance:** phase locks, read-only guarantees, validation phases, capital readiness, suppression policies, epistemic validation placeholders.

---

## 4. Current operational story

The repository currently describes this intended flow:

```text
Market data / news / broker inputs
        ↓
Ingestion + data normalization
        ↓
Research/intelligence layers and momentum/regime/narrative engines
        ↓
Evaluation, portfolio intelligence, and governance gates
        ↓
Dashboard loaders + reports + observation workflows
        ↓
Validation, audit, and scheduler/automation wrappers
```

That flow is conceptually strong, but the implementation is not yet wired as one dependable runtime. Multiple modules have their own runners, CLIs, validations, dashboards, and docs. The current practical question is therefore: **which path is the canonical daily cycle?**

A pragmatic canonical cycle should be chosen and made executable:

```text
1. Load/refresh market artifacts
2. Validate ingestion artifacts
3. Run research/intelligence stages for the selected market
4. Run evaluation/evolution bundle
5. Write canonical docs/intelligence and reports artifacts
6. Refresh dashboard API/frontend views from those artifacts
7. Run phase validation and daily validation review
```

Until that cycle is executable from one command and documented in one place, new feature work will keep adding more disconnected surfaces.

---

## 5. Confirmed gaps and risks

### 5.1 Critical gaps

| ID | Gap | Evidence | Impact | Recommended action |
| --- | --- | --- | --- | --- |
| G-01 | No single authoritative repository map | README, `docs/IMPLEMENTATION_STATUS.md`, `docs/System_Backlog_and_Refinements.md`, memory docs, dashboard specs, and architecture docs overlap. | Developers cannot tell which path is canonical. | Promote this document into the navigation layer and update `docs/README.md`/README to point to one current map. |
| G-02 | Validation artifacts missing | Ingestion validation failed with `missing_ingestion_artifacts` for raw, processed, and US artifacts. | The system cannot prove current data readiness. | Decide whether to commit fixtures, regenerate local artifacts, or adjust validation to support fixture mode vs live mode. |
| G-03 | Dependency/environment mismatch | `pytest --collect-only` failed on missing packages such as `pandas`, `pydantic`, `psycopg2`; validation skipped pandas-dependent checks. | Tests and validators do not provide a trustworthy signal. | Create a supported Python version/dependency setup and a minimal CI test target that can pass on a clean clone. |
| G-04 | Test collection is broken globally | `pytest --collect-only -q` stopped with 57 collection errors. | Full-suite regression testing cannot be used before implementation. | Split test suites by phase/domain, quarantine stale `_delete` tests, and fix import-time side effects/phase locks. |
| G-05 | Phase locks block test/import collection | Paper trading and some research modules intentionally raise at import unless phase env vars are set. | Expected safety controls are interfering with test discovery. | Move phase-lock assertions behind constructors/entrypoints or configure tests to set phase env before import. |
| G-06 | Canonical dashboard unclear | `dashboard/` static files coexist with `src/dashboard/backend` and `src/dashboard/frontend`. | UI changes may land in the wrong dashboard. | Declare `src/dashboard` as canonical or preserve static dashboard as legacy/read-only. |
| G-07 | Epistemic CI validator is a placeholder | `scripts/epistemic_validator.py` currently exits successfully after printing placeholder messages. | CI may pass while governance checks are not actually enforced. | Replace placeholder with concrete checks or rename it as a smoke placeholder until implemented. |
| G-08 | Historical/generated folders obscure source | `_delete`, `logs`, runtime reports, data artifacts, screenshots, and generated docs are intermixed with source. | Repo navigation and review become noisy; stale files may be collected as tests. | Formalize ignore/archive policy and remove/quarantine stale executable files. |

### 5.2 Wiring gaps

| Area | Missing wiring | Why it matters |
| --- | --- | --- |
| Ingestion → validation | Validators expect canonical raw/processed artifacts, but those artifacts are not currently present in this checkout/environment. | Cannot know whether ingestion is healthy. |
| Ingestion → research stages | US/India ingestion, research modules, and `src/ingestion` need one declared handoff contract. | Reduces duplicate loaders and schema drift. |
| Research → evaluation | Research modules and `src/evolution` both exist, but the daily driver should say which outputs feed evaluation. | Prevents disconnected research signals. |
| Evaluation → dashboard | Dashboard loaders read JSON/docs artifacts; the producing jobs must be listed and run before dashboard refresh. | Prevents stale or fake dashboard state. |
| Portfolio/broker → intelligence | Portfolio, Zerodha, broker connector/MCP docs exist, but live auth and fallback behavior need a safe operational path. | Prevents accidental execution or brittle refreshes. |
| Validation → scheduler | Scheduler wrapper can invoke validation review, but phase summaries must be created first and failures should have ownership. | Enables reliable daily health reports. |
| Automation agents → core repo | Jules/Gemini/autonomous loop code exists, but its trust boundary and allowed write scope need to be explicit. | Prevents automation from amplifying repo drift. |

---

## 6. What appears usable now

The repository is not a blank slate. Useful assets already exist and should be preserved:

1. **Conceptual architecture:** README and architecture docs describe a disciplined research/observation system.
2. **Validation framework:** `traderfund.validation` has phase tasks, component maps, diagnosis, remediation proposals, and persisted summaries.
3. **Dashboard foundation:** React/Vite frontend and FastAPI backend directories exist with loaders for intelligence, strategies, narrative, macro, portfolio, capital, provenance, temporal, and system status.
4. **Regime/narrative governance:** There are tests and modules for regime enforcement, accumulation, narrative genesis, strategy gates, suppression states, and audit artifacts.
5. **Portfolio intelligence documentation:** Extensive docs define exposure, look-through holdings, broker connectors, guidance generation, risk flags, and dashboard specs.
6. **Automation/hardening:** There are schedulers, drift detection, alerting, autonomous loop, semantic validators, and agent executors.

The near-term goal should be to wire and validate these assets, not to invent a new architecture.

---

## 7. Proposed recovery plan

### Phase A — Repository stabilization

**Goal:** make the repo inspectable and testable.

Tasks:

1. Add/update a top-level navigation section in README pointing to this assessment and the canonical docs.
2. Decide whether `_delete` should be excluded from pytest discovery, archived outside the repo, or removed.
3. Add pytest configuration to constrain default test discovery to supported test paths.
4. Create a clean environment setup target for backend tests.
5. Pin/verify Python version compatibility. The current environment used Python 3.14.4, while CI workflows reference Python 3.10 and 3.12.
6. Separate dependency groups: core runtime, dashboard/API, broker integrations, research-heavy dependencies, and dev/test.

Exit criteria:

- `python -m pytest --collect-only -q` succeeds for the selected default suite.
- `python -m traderfund.validation.validation_runner --phase ingestion --hook audit --market US` either passes in fixture mode or fails with one documented expected live-data prerequisite.
- README clearly says which docs are authoritative.

### Phase B — Canonical pipeline selection

**Goal:** define one daily cycle.

Tasks:

1. Choose one daily entrypoint: either extend `infra_hardening/scheduler/wrapper.py`, create a new `traderfund.pipeline.daily`, or promote an existing script.
2. Define market modes: `US`, `INDIA`, and fixture/demo mode.
3. Define canonical artifact locations for raw, processed, research outputs, intelligence state, evaluation bundles, reports, and dashboard inputs.
4. Make validation read the same artifact contract.
5. Add a dry-run command that exercises the whole cycle without broker/live API credentials.

Exit criteria:

- One documented command can run the daily pipeline in fixture/dry-run mode.
- Each stage emits an artifact manifest.
- Validation consumes the manifest rather than guessing file locations.

### Phase C — Dashboard authority and freshness

**Goal:** make the dashboard reflect canonical system state.

Tasks:

1. Declare `src/dashboard/backend` + `src/dashboard/frontend` as canonical unless the old `dashboard/` folder is intentionally retained.
2. Map every dashboard loader to the producer job and artifact it reads.
3. Add visible freshness/provenance fields for each dashboard panel.
4. Add a dashboard smoke test that validates backend endpoints and frontend build.

Exit criteria:

- `npm run build` succeeds in `src/dashboard/frontend`.
- Backend loaders can run in fixture mode.
- Dashboard panels show data freshness and missing-data reasons.

### Phase D — Governance and safety hardening

**Goal:** preserve safety while restoring developer velocity.

Tasks:

1. Convert placeholder epistemic validation into concrete checks.
2. Keep phase locks, but avoid import-time errors that break test collection.
3. Define allowed operations for broker integrations and paper trading.
4. Add capital/execution invariants to the default safety suite.
5. Document which modules are research-only, observation-only, paper-only, and live-forbidden.

Exit criteria:

- CI fails only on meaningful policy violations.
- Test discovery does not require unsafe phase changes.
- Broker/live execution paths remain gated and auditable.

### Phase E — Product backlog refresh

**Goal:** turn the gap register into implementation tasks.

Tasks:

1. Merge `docs/IMPLEMENTATION_STATUS.md` and `docs/System_Backlog_and_Refinements.md` into one current backlog or explicitly label one as historical.
2. Split backlog into: stabilization, wiring, dashboard, data, intelligence, governance, and future research.
3. Add owners/status/date fields to each item.
4. Create one near-term milestone: **“Fixture-mode daily pipeline + trustworthy validation.”**

Exit criteria:

- Every task has a concrete file/module target and acceptance check.
- Future feature work depends on the stabilization milestone.

---

## 8. Recommended priority backlog

| Priority | Task | Acceptance check |
| --- | --- | --- |
| P0 | Add pytest configuration to stop collecting `_delete` and unsupported phase-locked modules by default. | `python -m pytest --collect-only -q` succeeds for the default suite. |
| P0 | Fix dependency/bootstrap story. | A clean setup command installs all dependencies needed by default validation/tests. |
| P0 | Define fixture-mode data artifacts. | Ingestion validation can pass without live credentials when fixture mode is selected. |
| P0 | Declare canonical dashboard path. | README and docs state whether `src/dashboard` or `dashboard/` is authoritative. |
| P1 | Build one daily pipeline dry-run. | One command produces an artifact manifest and validation summaries. |
| P1 | Wire dashboard loaders to producer manifests. | Every dashboard panel has producer/freshness/missing-data metadata. |
| P1 | Replace epistemic placeholder. | CI guardrail performs concrete repo/document/policy checks. |
| P1 | Reconcile documentation authority. | README points to one current assessment, one architecture, one backlog, and one runbook. |
| P2 | Move phase-lock failures out of import-time paths where possible. | Phase-locked packages can be imported for tests/docs without enabling execution. |
| P2 | Archive generated/historical outputs. | Repo source tree no longer exposes stale test files or obsolete generated reports as active code. |

---

## 9. Immediate implementation sequence

If implementation starts after this assessment, do it in this order:

1. **Testing and environment reset**
   - Add pytest discovery config.
   - Confirm supported Python version.
   - Add/repair dependency install instructions.
2. **Fixture-mode validation**
   - Add small canonical raw/processed fixtures or teach validators to use existing fixture artifacts.
   - Make ingestion validation pass in fixture mode.
3. **Documentation navigation**
   - Update README/docs index to reference this document and label older docs as historical/current.
4. **Canonical daily pipeline dry-run**
   - Create one command that runs no live trading and no broker writes.
   - Emit manifests and validation summaries.
5. **Dashboard freshness wiring**
   - Connect dashboard loaders to manifest-backed artifacts.
6. **Governance/CI hardening**
   - Replace placeholder checks and preserve phase/capital safety.

---

## 10. Definition of done for the recovery effort

The repository can be considered back under control when all of the following are true:

- A new developer can read README and know the canonical architecture, backlog, and runbook.
- A clean clone can install dependencies using one documented command.
- Default test collection succeeds.
- Fixture-mode ingestion validation succeeds.
- One dry-run daily pipeline command completes without live credentials.
- Dashboard backend/frontend can start from fixture artifacts.
- Every dashboard panel can explain freshness and missing data.
- Phase locks prevent unsafe operations without breaking imports and test discovery.
- CI validates real governance checks, not placeholders.

---

## 11. Open decisions

These decisions should be made before feature work resumes:

1. **Canonical market priority:** Is the next milestone US-first, India-first, or dual-market fixture mode?
2. **Canonical dashboard:** Should `dashboard/` be archived as legacy and `src/dashboard` become the only maintained UI?
3. **Canonical data contract:** Which artifact paths are mandatory for raw, processed, research, evaluation, and dashboard state?
4. **Dependency policy:** Should heavyweight packages such as TensorFlow be part of the base install, or moved to an optional research extra?
5. **Phase-lock policy:** Should phase locks be import-time gates or runtime execution gates?
6. **Generated artifact policy:** Which outputs belong in git, and which belong in ignored runtime/artifact storage?
7. **Automation trust boundary:** Which automation agents may modify code, and what validation must pass before merge?

---

## 12. Bottom line

TraderFund has a substantial amount of useful code and design work, but it needs a stabilization milestone before more implementation. The next work should not start with another feature. It should start with repository control: test discovery, dependency setup, fixture-mode validation, canonical pipeline wiring, dashboard authority, and documentation reconciliation.

Once those are in place, feature implementation can proceed with confidence because every change will have an executable path, a validation signal, and a visible dashboard/reporting destination.
