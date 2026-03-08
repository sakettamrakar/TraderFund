from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List

from .validation_engine import ValidationResult


@dataclass(slots=True)
class Diagnosis:
    phase: str
    task: str
    root_cause: str
    severity: str
    explanation: str
    llm_explanation: str = ""
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DiagnosisEngine:
    _ROOT_CAUSE_MAP: Dict[tuple[str, str], tuple[str, str, str]] = {
        ("ingestion", "schema_validation"): ("ingestion_parser_issue", "high", "Schema drift indicates the ingestion contract or canonical normalization path is out of sync."),
        ("ingestion", "timestamp_validation"): ("source_feed_time_error", "high", "Timestamp validation failed, which usually means feed-time normalization or source clock handling regressed."),
        ("ingestion", "null_handling"): ("incomplete_normalization", "medium", "Nulls or duplicates indicate the canonical transform is not fully fail-closing malformed records."),
        ("ingestion", "data_lineage"): ("lineage_contract_gap", "medium", "Lineage evidence is missing, so downstream consumers cannot trace ingestion outputs back to their source contracts."),
        ("memory", "layer_routing"): ("memory_routing_contract_gap", "high", "The V3 memory routing layer is missing required canonical stores or reports."),
        ("memory", "mutation_control"): ("mutation_audit_gap", "high", "Mutation control evidence is incomplete, so overwrite behavior is not fully auditable."),
        ("memory", "cross_layer_contamination"): ("cross_layer_authority_collision", "high", "Duplicate authority artifacts create contamination between canonical memory layers."),
        ("research", "factor_determinism"): ("factor_computation_inconsistency", "high", "Factor computation should be deterministic for identical inputs and no longer is."),
        ("research", "regime_gating"): ("regime_gate_missing", "critical", "Downstream research is no longer fail-closing when regime context is absent."),
        ("research", "reproducibility"): ("research_output_nondeterminism", "high", "Repeated research execution is generating unstable outputs or hashes."),
        ("evaluation", "score_consistency"): ("evaluation_artifact_drift", "high", "Evaluation artifacts are incomplete or inconsistent with the active pipeline."),
        ("evaluation", "evolution_integrity"): ("shadow_governance_violation", "critical", "Evaluation profiles lost the required shadow-only protections."),
        ("dashboard", "traceability"): ("dashboard_provenance_gap", "high", "Dashboard payloads lost required provenance fields and can no longer be audited."),
        ("dashboard", "freshness"): ("truth_epoch_freshness_gap", "high", "Dashboard freshness signals no longer bind cleanly to the live truth epoch and temporal state."),
        ("dashboard", "read_only_guarantee"): ("dashboard_mutability_risk", "critical", "The dashboard surface is no longer provably read-only."),
    }

    def diagnose(self, results: Iterable[ValidationResult]) -> List[Diagnosis]:
        diagnoses: List[Diagnosis] = []
        for result in results:
            if result.status != "FAIL":
                continue
            root_cause, severity, explanation = self._ROOT_CAUSE_MAP.get(
                (result.phase, result.task),
                ("unknown_validation_failure", "medium", "Validation failed without a specialized diagnosis mapping."),
            )
            diagnoses.append(
                Diagnosis(
                    phase=result.phase,
                    task=result.task,
                    root_cause=root_cause,
                    severity=severity,
                    explanation=explanation,
                    llm_explanation=self._explain_with_llm(result, root_cause, explanation),
                    evidence=list(result.evidence),
                )
            )
        return diagnoses

    def _explain_with_llm(self, result: ValidationResult, root_cause: str, fallback: str) -> str:
        llm_enabled = bool(os.getenv("VALIDATION_ENABLE_LLM")) or bool(os.getenv("MOCK_GEMINI")) or bool(os.getenv("LLM_MODEL_PATH"))
        if not llm_enabled:
            return ""

        prompt = (
            "Explain this TraderFund validation failure in 2-3 sentences. "
            f"Phase={result.phase}; task={result.task}; root_cause={root_cause}; "
            f"reason={result.reason}; details={result.details}."
        )

        try:
            from llm_integration.client import get_llm_client

            client = get_llm_client()
            if client is not None:
                return client.generate(
                    "You explain validation failures for a trading research platform. Be concrete and brief.",
                    prompt,
                    max_tokens=200,
                )
        except Exception:
            pass

        try:
            from automation.gemini_bridge import ask

            return ask(prompt)
        except Exception:
            return fallback