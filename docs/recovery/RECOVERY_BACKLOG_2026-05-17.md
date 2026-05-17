# Recovery Backlog: Repository Stabilization

**Status:** CURRENT  
**Created:** 2026-05-17  
**Owner:** TBD  
**Source DWBS:** `docs/architecture/DWBS_REPOSITORY_RECOVERY_2026-05-17.md`  
**Source Assessment:** `docs/CURRENT_REPOSITORY_ASSESSMENT.md`  
**Active Milestone:** Fixture-mode daily pipeline + trustworthy validation  

---

## 1. Authority

This is the current execution backlog for repository recovery work. It replaces
older mixed status/backlog documents for task picking.

Current references:

| Document | Role |
| :--- | :--- |
| `docs/CURRENT_REPOSITORY_ASSESSMENT.md` | Current repository situation and gap register |
| `docs/architecture/DWBS_REPOSITORY_RECOVERY_2026-05-17.md` | Recovery task breakdown and dependencies |
| `docs/recovery/RECOVERY_BACKLOG_2026-05-17.md` | Current pickable backlog |
| `docs/recovery/ARCHIVE_AND_IGNORE_POLICY_2026-05-17.md` | Archive, ignore, and evidence policy |
| `docs/RUNBOOK.md` | Operational commands and recovery validation |

Historical or reference-only documents:

| Document | Current Use |
| :--- | :--- |
| `docs/IMPLEMENTATION_STATUS.md` | Historical implementation snapshot; not the active backlog |
| `docs/System_Backlog_and_Refinements.md` | Historical refinement backlog; not the active recovery task list |
| `docs/VISION_BACKLOG.md` | Awareness-only vision inventory; not actionable |
| `docs/architecture/DWBS_INTELLIGENCE_IMPLEMENTATION.md` | Prior intelligence implementation reference until reconciled |

---

## 2. Active Milestone

**Milestone:** Fixture-mode daily pipeline + trustworthy validation  
**Milestone Status:** RECOVERY IMPLEMENTED, KEEP AS THE FEATURE-GATE BASELINE  
**Gate Rule:** No new roadmap expansion should start unless this milestone remains
green or the team explicitly records a decision to defer a failing check.

Milestone closure checks:

| Check | Current Status | Verification |
| :--- | :--- | :--- |
| Default test collection completes | DONE | `python -m pytest --collect-only -q` |
| Default dependencies are documented | DONE | `README.md`, `requirements.txt`, `requirements/` |
| Fixture ingestion validation passes | DONE | `python -m traderfund.validation.validation_runner --phase ingestion --hook manual --market fixture` |
| Fixture daily pipeline emits manifest and validation summary | DONE | `python -m traderfund.pipeline.daily --market fixture` |
| Dashboard authority is declared | DONE | `README.md`, `dashboard/ARCHIVED.md` |
| Dashboard exposes freshness and provenance | DONE | `docs/dashboard/LOADER_ARTIFACT_MAP.md`, backend loaders |
| Governance checks are concrete | DONE | `python scripts/epistemic_validator.py --mode strict` |
| Phase locks are import-safe | DONE | pytest collection and targeted phase-lock tests |
| Broker/live execution is gated | DONE | `docs/governance/OPERATIONAL_BOUNDARIES_AND_SAFETY.md` |
| One current backlog exists | DONE | This file |

---

## 3. Recovery Lanes

Each task appears in exactly one lane. Owner is intentionally left as `TBD`
until the team assigns implementation ownership.

### Stabilization Lane

| Task | Status | Owner | Date | Acceptance Check |
| :--- | :--- | :--- | :--- | :--- |
| RR-A.1 Establish Current Navigation Authority | DONE | TBD | 2026-05-17 | README links the assessment, DWBS, backlog, and runbook. |
| RR-A.2 Define Default Test Discovery Boundary | DONE | TBD | 2026-05-17 | `python -m pytest --collect-only -q` completes for the selected default suite. |
| RR-A.3 Repair Dependency and Environment Bootstrap | DONE | TBD | 2026-05-17 | Default dependency installation is documented and works in a clean environment. |
| RR-A.4 Restore Default Test Collection Signal | DONE | TBD | 2026-05-17 | Default pytest collection exits successfully. |
| RR-A.6 Classify Generated and Historical Artifacts | DONE | TBD | 2026-05-17 | Generated/runtime outputs are ignored or documented as evidence/reference. |

### Data Lane

| Task | Status | Owner | Date | Acceptance Check |
| :--- | :--- | :--- | :--- | :--- |
| RR-A.5 Define Fixture-Mode Ingestion Artifacts | DONE | TBD | 2026-05-17 | Fixture-mode ingestion validation passes without live credentials. |

### Wiring Lane

| Task | Status | Owner | Date | Acceptance Check |
| :--- | :--- | :--- | :--- | :--- |
| RR-B.1 Choose the Daily Pipeline Entrypoint | DONE | TBD | 2026-05-17 | One documented daily pipeline command is authoritative. |
| RR-B.2 Define Market Modes | DONE | TBD | 2026-05-17 | Fixture mode runs without credentials and live modes fail explicitly unless dry-run. |
| RR-B.3 Define Canonical Artifact Contract | DONE | TBD | 2026-05-17 | Manifest entries include producer, path, schema/version, timestamp, and market mode. |
| RR-B.4 Wire Validation to the Artifact Manifest | DONE | TBD | 2026-05-17 | Validation resolves fixture artifacts from the manifest. |
| RR-B.5 Build Fixture-Mode Daily Dry Run | DONE | TBD | 2026-05-17 | `python -m traderfund.pipeline.daily --market fixture` succeeds. |

### Dashboard Lane

| Task | Status | Owner | Date | Acceptance Check |
| :--- | :--- | :--- | :--- | :--- |
| RR-C.1 Declare Canonical Dashboard Surface | DONE | TBD | 2026-05-17 | `src/dashboard` is documented as canonical and `dashboard/` is archived. |
| RR-C.2 Map Dashboard Loaders to Producer Artifacts | DONE | TBD | 2026-05-17 | Dashboard loader map documents producer, artifact, schema, and missing-data behavior. |
| RR-C.3 Add Freshness and Provenance Metadata | DONE | TBD | 2026-05-17 | Dashboard responses expose freshness/provenance or missing-data reason. |
| RR-C.4 Add Dashboard Fixture Smoke Test | DONE | TBD | 2026-05-17 | Backend fixture smoke tests and frontend build pass. |

### Governance Lane

| Task | Status | Owner | Date | Acceptance Check |
| :--- | :--- | :--- | :--- | :--- |
| RR-D.1 Replace Epistemic Placeholder Validation | DONE | TBD | 2026-05-17 | `scripts/epistemic_validator.py` performs concrete checks and fails on violations. |
| RR-D.2 Move Phase-Lock Failures Out of Harmless Imports | DONE | TBD | 2026-05-17 | Phase-locked packages import during test discovery without enabling execution. |
| RR-D.3 Define Broker and Paper-Trading Operation Boundaries | DONE | TBD | 2026-05-17 | Operational boundaries identify research-only, paper-only, observation-only, and live-forbidden paths. |
| RR-D.4 Add Capital and Execution Safety Checks | DONE | TBD | 2026-05-17 | Safety validation detects forbidden broker/order/capital write surfaces. |
| RR-D.5 Define Automation Agent Trust Boundary | DONE | TBD | 2026-05-17 | Automation write scopes, forbidden areas, and readiness gates are documented. |

### Documentation Lane

| Task | Status | Owner | Date | Acceptance Check |
| :--- | :--- | :--- | :--- | :--- |
| RR-E.1 Reconcile Current Status and Backlog Documents | DONE | TBD | 2026-05-17 | README points to one current backlog and labels older docs as historical/reference. |
| RR-E.2 Split Backlog by Recovery Lanes | DONE | TBD | 2026-05-17 | Every RR task appears in exactly one lane with status, owner, date, and acceptance check. |
| RR-E.3 Apply Archive/Ignore Policy | DONE | TBD | 2026-05-17 | Runtime/generated artifacts are ignored or explicitly classified, and evidence remains traceable. |
| RR-E.4 Declare the Next Implementation Milestone | DONE | TBD | 2026-05-17 | Feature work depends on this milestone staying green or a recorded defer decision. |

### Intelligence Lane

There are no active recovery tasks in this lane. Intelligence feature work stays
blocked until the active milestone remains green and a separate roadmap decision
promotes work from historical or vision documents.

### Future Research Lane

Historical and conceptual candidates live in `docs/System_Backlog_and_Refinements.md`
and `docs/VISION_BACKLOG.md`. They are not pickable until copied into a current
roadmap with explicit acceptance checks and governance approval.

---

## 4. Next Pick Rule

The next implementation task after this recovery backlog must start from one of:

1. A new dated DWBS file.
2. A new current roadmap file that explicitly references this recovery backlog.
3. A recorded decision that defers a failing recovery gate.

Do not pick directly from historical or vision documents.
