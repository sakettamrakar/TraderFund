# Memory Quality Contract

## Purpose

Project memory is **externalized cognition** shared between humans and AI agents. It is the single persistent substrate that carries intent, decisions, constraints, and non-goals across sessions, contributors, and tools. Without high-quality memory, every conversation starts from zero. Code can be regenerated; lost intent cannot.

---

## Invariants

### 1. Authority Invariant
Every document has exactly one authoritative owner (human or role). No two documents may authoritatively define the same concern.
> **PASS/FAIL:** _Can you point to exactly one file that owns this concern, and does it name its authority?_

### 2. Explicit Exclusion Invariant
What the system will **not** do is as important as what it will do. Non-goals must be written, not implied.
> [!NOTE] AUDIT: Defines quality requirement for Scope; actual Scope is owned by boundaries.md.
> **PASS/FAIL:** _Are non-goals explicitly listed, or must a reader infer them?_

### 3. Decision Traceability Invariant
Every significant decision is recorded with its rationale and date. Decisions are never silently overwritten.
> **PASS/FAIL:** _Can you trace why a particular design choice was made and when?_

### 4. Intent vs Implementation Separation
**Why** something exists (intent) must be separated from **how** it is built (code). Intent documents survive rewrites; code does not survive lost intent.
> **PASS/FAIL:** _If all code were deleted, could the system be rebuilt from memory alone?_

### 5. Machine Parsability Invariant
Memory artifacts must be structured enough for automated tools and LLMs to consume without ambiguity. Use consistent formats, headings, and naming conventions.
> **PASS/FAIL:** _Can a script or LLM reliably extract key facts from this document without human guidance?_

### 6. Drift Detection Invariant
When memory and reality diverge, the divergence must be detectable. Stale, contradictory, or orphaned documents are memory corruption.
> **PASS/FAIL:** _Is there a way to detect that this document no longer reflects the true system state?_

### 7. Update Locality Invariant
Changing a fact should require updating exactly one place. If a change requires edits in multiple files, the structure is wrong.
> **PASS/FAIL:** _Does updating this fact require touching more than one document?_

### 8. Regeneration Safety Invariant
Any generated or derived artifact must be safely reproducible from authoritative memory. Deleting generated outputs must not cause information loss.
> **PASS/FAIL:** _If this file were deleted, could it be fully regenerated from other memory artifacts?_

---

## Quality Checklist

- [ ] Single source of truth per concern
- [ ] Non-goals written
- [ ] Decisions recorded
- [ ] Intent separated from code
- [ ] Machine readable structure
- [ ] No contradictions
- [ ] Obvious update paths
- [ ] Regenerable from memory

---

## Rules

1. **LLMs may NEVER modify** vision, scope, success criteria, or recorded decisions.
2. **Humans are the final authority** on specifications, priorities, and constraints.
3. **Memory is more important than code.** Code implements; memory defines. Protect memory first.
