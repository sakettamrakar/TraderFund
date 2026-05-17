# Archive and Ignore Policy

**Status:** CURRENT  
**Created:** 2026-05-17  
**Owner:** TBD  
**Source Task:** RR-E.3 in `docs/architecture/DWBS_REPOSITORY_RECOVERY_2026-05-17.md`

---

## 1. Purpose

This policy keeps active source navigation clean while preserving useful
evidence. It classifies artifacts as active source, committed evidence,
historical reference, or ignored runtime output.

---

## 2. Classification Rules

| Class | Rule | Examples |
| :--- | :--- | :--- |
| Active source | Code, tests, contracts, and current docs required for default operation. | `src/`, `tests/`, `traderfund/`, `docs/contracts/`, `docs/recovery/` |
| Committed evidence | Small, intentional artifacts needed for fixture validation or auditability. | `data/fixtures/`, `docs/intelligence/temporal/temporal_state_fixture.json` |
| Historical reference | Useful but not pickable as current work. Must be labeled as historical/reference. | `docs/IMPLEMENTATION_STATUS.md`, `docs/System_Backlog_and_Refinements.md` |
| Awareness only | Conceptual inventory that cannot create implementation work directly. | `docs/VISION_BACKLOG.md` |
| Ignored runtime output | Regenerable logs, reports, local state, graph output, and bulky generated artifacts. | `logs/`, `.runtime/`, `artifacts/`, `generated/`, `reports/`, `graphify-out/` |
| Archived/stale surface | Old source-like folders retained only as reference unless explicitly reactivated. | `_delete/`, `analysis/`, `analytics/`, `research_audit/`, `research_reports/`, `alpha_discovery/`, `presentation/` |

---

## 3. Git Ignore Baseline

The repository `.gitignore` should continue to ignore:

- raw and processed data by default,
- runtime logs and local state,
- high-volume generated reports,
- Graphify output,
- stale archived surfaces,
- local debug scripts and patch files.

The repository should explicitly keep:

- `data/fixtures/**` for fixture validation,
- current documentation under `docs/recovery/`, `docs/contracts/`, `docs/dashboard/`, and `docs/governance/`,
- small temporal fixture truth artifacts used by dashboard validation.

---

## 4. Evidence Rule

Do not delete evidence just to reduce noise. If an artifact proves a recovery
decision, either keep it in a clearly documented location or ignore it as
regenerable runtime output. If an old doc contains useful context but is no
longer authoritative, add a status banner instead of silently removing it.

---

## 5. Reactivation Rule

A historical or archived document can become actionable only when a new dated
DWBS or roadmap copies the task into a current backlog with:

- owner placeholder,
- date,
- status,
- acceptance check,
- dependency and safety impact.
