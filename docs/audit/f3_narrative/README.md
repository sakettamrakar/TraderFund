# F3 Narrative Audit Logs

Append-only logs for narrative leakage remediation (`F3`).

- `narrative_suppressions.jsonl`: emitted when narrative output is gated (`SILENCED`, `CAUSAL_ONLY`, or `EVIDENCE_ONLY`).
- `language_violations.jsonl`: emitted when banned narrative language is detected and output is blocked.
- `narrative_mode_transitions.jsonl`: emitted when narrative mode changes between evaluations.
