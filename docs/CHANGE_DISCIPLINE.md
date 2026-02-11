# Change Discipline

Minimal rules to keep changes reversible and memory safe.

---

## 1. Branching

- Do not commit directly to `main`.
- All changes go through a pull request.
- Keep PRs small. One concern per PR.

## 2. Rollback

- The previous commit is your rollback plan.
- If something breaks, **revert first**, investigate second.
- Prefer `git revert` over hasty hotfixes.

## 3. Memory Protection

- Everything under `docs/memory/` is authoritative project memory.
- Changes to memory files require **human review** before merge.
- AI may propose changes to memory. AI may **not** auto-merge them.
- When in doubt, leave memory untouched.

## 4. Audit Hook

- Run `python scripts/memory_audit.py` before merging any PR that touches `docs/memory/`.
- If the audit shows new FAILs, do not merge until resolved.
- WARNs are acceptable — they surface risks, not blockers.

## 5. Common Sense

- If a change feels too big, split it.
- If a revert feels scary, the change was too big.
- Ship boring, reversible changes. Save courage for the vision.
