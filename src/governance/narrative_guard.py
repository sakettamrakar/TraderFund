"""
F3 Narrative Governance Guard.

Implements narrative leakage controls with explicit narrative modes:
- SILENCED
- CAUSAL_ONLY
- EVIDENCE_ONLY
- EXPLANATORY

Safety invariants:
- No execution/capital enablement.
- No Truth Epoch advancement.
- No override of suppression (F5) or regime degradation (F2).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from governance.suppression_state import compute_suppression_for_market
except Exception:
    from src.governance.suppression_state import compute_suppression_for_market  # type: ignore

PROJECT_ROOT = Path(__file__).parent.parent.parent
INTEL_DIR = PROJECT_ROOT / "docs" / "intelligence"
TEMPORAL_DIR = INTEL_DIR / "temporal"
EVOLUTION_CONTEXT_DIR = PROJECT_ROOT / "docs" / "evolution" / "context"
AUDIT_DIR = PROJECT_ROOT / "docs" / "audit" / "f3_narrative"

CANONICAL_COMPLETE = "CANONICAL_COMPLETE"

NARRATIVE_MODES = ["SILENCED", "CAUSAL_ONLY", "EVIDENCE_ONLY", "EXPLANATORY"]

BANNED_TERMS: List[Dict[str, str]] = [
    {"term": "buy", "category": "ACTION_VERB"},
    {"term": "sell", "category": "ACTION_VERB"},
    {"term": "enter", "category": "ACTION_VERB"},
    {"term": "exit", "category": "ACTION_VERB"},
    {"term": "strong", "category": "CONFIDENCE_ESCALATION"},
    {"term": "clear", "category": "CONFIDENCE_ESCALATION"},
    {"term": "likely", "category": "CONFIDENCE_ESCALATION"},
    {"term": "expected", "category": "CONFIDENCE_ESCALATION"},
    {"term": "soon", "category": "TEMPORAL_PROMISE"},
    {"term": "setting up", "category": "TEMPORAL_PROMISE"},
    {"term": "about to", "category": "TEMPORAL_PROMISE"},
    {"term": "best", "category": "OPTIMIZATION_LANGUAGE"},
    {"term": "opportunity", "category": "OPTIMIZATION_LANGUAGE"},
    {"term": "edge", "category": "OPTIMIZATION_LANGUAGE"},
    {"term": "therefore", "category": "CAUSAL_CLOSURE"},
    {"term": "hence", "category": "CAUSAL_CLOSURE"},
    {"term": "this means", "category": "CAUSAL_CLOSURE"},
]


def _utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return {}


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


def _hash_payload(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _load_truth_epoch(market: str) -> str:
    temporal = _read_json(TEMPORAL_DIR / f"temporal_state_{market}.json")
    epoch = temporal.get("temporal_state", {}).get("truth_epoch", {}) or {}
    if epoch.get("epoch_id"):
        return str(epoch.get("epoch_id"))
    if epoch.get("timestamp"):
        return f"TE-{epoch.get('timestamp')}"

    global_epoch = _read_json(PROJECT_ROOT / "docs" / "epistemic" / "truth_epoch.json")
    eid = global_epoch.get("epoch", {}).get("epoch_id")
    return str(eid) if eid else "TE-2026-01-30"


def _load_suppression_bundle(market: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    state_path = INTEL_DIR / f"suppression_state_{market}.json"
    registry_path = INTEL_DIR / f"suppression_reason_registry_{market}.json"
    state = _read_json(state_path)
    registry = _read_json(registry_path)

    if not state or not registry:
        computed = compute_suppression_for_market(market)
        state = computed.get("summary", {})
        registry = computed.get("registry", {})
    return state, registry


def _scan_language_violations(text: str) -> List[Dict[str, str]]:
    violations: List[Dict[str, str]] = []
    lowered = text.lower()

    for entry in BANNED_TERMS:
        term = entry["term"]
        category = entry["category"]

        if " " in term:
            hit = term in lowered
        else:
            hit = re.search(rf"\b{re.escape(term)}\b", lowered) is not None

        if hit:
            violations.append({"term": term, "category": category})

    seen = set()
    unique: List[Dict[str, str]] = []
    for item in violations:
        key = (item["term"], item["category"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _extract_regime_state(policy: Dict[str, Any], regime_ctx: Dict[str, Any]) -> Tuple[str, str, str]:
    regime_state = str(
        policy.get("regime_state")
        or regime_ctx.get("regime_state")
        or regime_ctx.get("regime_code")
        or regime_ctx.get("regime")
        or "UNKNOWN"
    ).upper()
    regime_confidence = str(
        policy.get("regime_confidence")
        or regime_ctx.get("regime_confidence")
        or regime_ctx.get("confidence")
        or "UNKNOWN"
    ).upper()
    regime_reason = str(
        policy.get("regime_reason")
        or regime_ctx.get("regime_reason")
        or "Regime reason unavailable."
    )
    return regime_state, regime_confidence, regime_reason


def _initial_mode(
    suppression_state: str,
    canonical_state: str,
    regime_state: str,
    regime_confidence: str,
) -> str:
    if suppression_state != "NONE":
        return "CAUSAL_ONLY"
    if canonical_state != CANONICAL_COMPLETE:
        return "EVIDENCE_ONLY"
    if regime_state in {"UNKNOWN", "DEGRADED"} or regime_confidence == "DEGRADED":
        return "EVIDENCE_ONLY"
    return "EXPLANATORY"


def _build_gating_reasons(
    suppression_state: str,
    suppression_primary: Dict[str, Any],
    canonical_state: str,
    regime_state: str,
    regime_confidence: str,
) -> List[Dict[str, str]]:
    reasons: List[Dict[str, str]] = []

    if suppression_state != "NONE":
        reasons.append(
            {
                "code": "SUPPRESSION_STATE_ACTIVE",
                "detail": (
                    f"ACTION BLOCKED DUE TO suppression state {suppression_state}"
                    f" ({suppression_primary.get('reason_id', 'UNSPECIFIED')})."
                ),
            }
        )

    if canonical_state != CANONICAL_COMPLETE:
        reasons.append(
            {
                "code": "CANONICAL_STATE_INCOMPLETE",
                "detail": f"Canonical state is {canonical_state}; explanatory narrative is disallowed.",
            }
        )

    if regime_state in {"UNKNOWN", "DEGRADED"} or regime_confidence == "DEGRADED":
        reasons.append(
            {
                "code": "REGIME_DEGRADED_OR_UNKNOWN",
                "detail": (
                    f"Regime state is {regime_state} with confidence {regime_confidence}; "
                    "directional or confidence language is disallowed."
                ),
            }
        )

    return reasons


def _build_material_facts(
    market: str,
    truth_epoch: str,
    temporal: Dict[str, Any],
    canonical: Dict[str, Any],
    policy: Dict[str, Any],
    regime_state: str,
    regime_confidence: str,
    regime_reason: str,
    suppression_state: Dict[str, Any],
    suppression_registry: Dict[str, Any],
) -> Dict[str, Any]:
    drift = temporal.get("drift_status", {}) or {}
    reasons = suppression_registry.get("reasons", []) or []

    return {
        "market": market,
        "truth_epoch": truth_epoch,
        "suppression_state": suppression_state.get("suppression_state", "NONE"),
        "suppression_reason_ids": [str(r.get("reason_id")) for r in reasons if r.get("reason_id")],
        "canonical_state": canonical.get("canonical_state", "UNKNOWN"),
        "canonical_missing_roles": canonical.get("missing_roles", []) or [],
        "canonical_stale_roles": canonical.get("stale_roles", []) or [],
        "regime_state": regime_state,
        "regime_confidence": regime_confidence,
        "regime_reason": regime_reason,
        "policy_state": str(policy.get("policy_state", "UNKNOWN")).upper(),
        "policy_permissions": sorted(policy.get("permissions", []) or []),
        "drift_status_code": str(drift.get("status_code", "UNKNOWN")),
        "evaluation_drift_days": int(drift.get("evaluation_drift_days", 0) or 0),
        "drift_limit_exceeded": bool(drift.get("drift_limit_exceeded", False)),
    }


def _changed_material_keys(previous: Dict[str, Any], current: Dict[str, Any]) -> List[str]:
    keys = sorted(set(previous.keys()) | set(current.keys()))
    changed: List[str] = []
    for key in keys:
        if previous.get(key) != current.get(key):
            changed.append(key)
    return changed


def _build_summary(
    mode: str,
    market: str,
    truth_epoch: str,
    suppression_state: str,
    primary_reason: Dict[str, Any],
    canonical_state: str,
    regime_state: str,
    regime_confidence: str,
) -> str:
    if mode == "CAUSAL_ONLY":
        return (
            f"ACTION BLOCKED DUE TO: {primary_reason.get('reason_id', 'UNSPECIFIED')}. "
            f"Market={market}; TruthEpoch={truth_epoch}; SuppressionState={suppression_state}; "
            f"CanonicalState={canonical_state}; RegimeState={regime_state}; RegimeConfidence={regime_confidence}. "
            "Execution and capital remain disabled."
        )

    if mode == "EVIDENCE_ONLY":
        return (
            "EVIDENCE ONLY: "
            f"Market={market}; TruthEpoch={truth_epoch}; "
            f"SuppressionState={suppression_state}; CanonicalState={canonical_state}; "
            f"RegimeState={regime_state}; RegimeConfidence={regime_confidence}. "
            "No directional inference is emitted."
        )

    if mode == "EXPLANATORY":
        return (
            "EXPLANATORY MODE: "
            f"Market={market} is reported with canonical-complete narrative eligibility at {truth_epoch}. "
            f"RegimeState={regime_state}; RegimeConfidence={regime_confidence}; SuppressionState={suppression_state}. "
            "Narrative remains descriptive and non-actionable."
        )

    return ""


def _tone_for_mode(mode: str) -> str:
    mapping = {
        "SILENCED": "NO_OUTPUT",
        "CAUSAL_ONLY": "CAUSAL",
        "EVIDENCE_ONLY": "EVIDENCE",
        "EXPLANATORY": "DESCRIPTIVE",
    }
    return mapping.get(mode, "UNKNOWN")


def _posture_for_mode(mode: str) -> str:
    mapping = {
        "SILENCED": "NARRATIVE_GATED",
        "CAUSAL_ONLY": "ACTION_BLOCKED",
        "EVIDENCE_ONLY": "OBSERVATIONAL",
        "EXPLANATORY": "OBSERVATIONAL",
    }
    return mapping.get(mode, "UNKNOWN")


def _collect_provenance_refs(market: str, suppression_registry: Dict[str, Any]) -> List[str]:
    refs = {
        f"docs/intelligence/suppression_state_{market}.json",
        f"docs/intelligence/suppression_reason_registry_{market}.json",
        f"docs/intelligence/canonical_partiality_state_{market}.json",
        f"docs/intelligence/decision_policy_{market}.json",
        f"docs/intelligence/temporal/temporal_state_{market}.json",
        f"docs/evolution/context/regime_context_{market}.json",
    }
    for reason in suppression_registry.get("reasons", []) or []:
        for src in reason.get("source_artifacts", []) or []:
            refs.add(str(src))
    return sorted(refs)


def compute_narrative_for_market(market: str) -> Dict[str, Any]:
    market = market.upper()
    now = _utc_now_iso()

    truth_epoch = _load_truth_epoch(market)
    temporal = _read_json(TEMPORAL_DIR / f"temporal_state_{market}.json")
    canonical = _read_json(INTEL_DIR / f"canonical_partiality_state_{market}.json")
    policy = _read_json(INTEL_DIR / f"decision_policy_{market}.json").get("policy_decision", {})
    regime_ctx = _read_json(EVOLUTION_CONTEXT_DIR / f"regime_context_{market}.json").get("regime_context", {})

    suppression_state, suppression_registry = _load_suppression_bundle(market)
    suppression_code = str(suppression_state.get("suppression_state", "NONE")).upper()
    primary_reason = suppression_state.get("primary_reason", {}) or {}

    canonical_state = str(
        canonical.get("canonical_state")
        or policy.get("canonical_state")
        or regime_ctx.get("canonical_state")
        or "UNKNOWN"
    ).upper()
    regime_state, regime_confidence, regime_reason = _extract_regime_state(policy, regime_ctx)

    mode = _initial_mode(
        suppression_state=suppression_code,
        canonical_state=canonical_state,
        regime_state=regime_state,
        regime_confidence=regime_confidence,
    )
    gating_reasons = _build_gating_reasons(
        suppression_state=suppression_code,
        suppression_primary=primary_reason,
        canonical_state=canonical_state,
        regime_state=regime_state,
        regime_confidence=regime_confidence,
    )

    material_facts = _build_material_facts(
        market=market,
        truth_epoch=truth_epoch,
        temporal=temporal,
        canonical=canonical,
        policy=policy,
        regime_state=regime_state,
        regime_confidence=regime_confidence,
        regime_reason=regime_reason,
        suppression_state=suppression_state,
        suppression_registry=suppression_registry,
    )
    material_facts_hash = _hash_payload(material_facts)

    state_path = INTEL_DIR / f"narrative_state_{market}.json"
    previous = _read_json(state_path)
    previous_mode = str(previous.get("narrative_mode", "UNKNOWN"))
    previous_hash = str(previous.get("material_facts_hash", ""))
    previous_epoch = str(previous.get("truth_epoch", ""))
    previous_facts = previous.get("material_facts", {}) or {}

    diff_status = "NO_BASELINE"
    changed_fields: List[str] = []
    if previous_hash:
        changed_fields = _changed_material_keys(previous_facts, material_facts)
        if previous_epoch == truth_epoch and previous_hash == material_facts_hash:
            diff_status = "UNCHANGED"
        else:
            diff_status = "CHANGED"

    if diff_status == "UNCHANGED":
        mode = "SILENCED"
        gating_reasons.append(
            {
                "code": "NO_MATERIAL_FACT_CHANGE",
                "detail": "No material factual change versus last Truth Epoch narrative snapshot.",
            }
        )

    summary = _build_summary(
        mode=mode,
        market=market,
        truth_epoch=truth_epoch,
        suppression_state=suppression_code,
        primary_reason=primary_reason,
        canonical_state=canonical_state,
        regime_state=regime_state,
        regime_confidence=regime_confidence,
    )

    language_violations = _scan_language_violations(summary)
    if language_violations:
        mode = "SILENCED"
        summary = ""
        gating_reasons.append(
            {
                "code": "LANGUAGE_POLICY_VIOLATION",
                "detail": "Narrative output blocked by hard language bans.",
            }
        )
        _append_jsonl(
            AUDIT_DIR / "language_violations.jsonl",
            {
                "event": "NARRATIVE_LANGUAGE_VIOLATION",
                "computed_at": now,
                "market": market,
                "truth_epoch": truth_epoch,
                "candidate_mode": _initial_mode(
                    suppression_state=suppression_code,
                    canonical_state=canonical_state,
                    regime_state=regime_state,
                    regime_confidence=regime_confidence,
                ),
                "violations": language_violations,
                "artifact": str(state_path.relative_to(PROJECT_ROOT)),
            },
        )

    silence_reason = None
    if mode == "SILENCED":
        if diff_status == "UNCHANGED":
            silence_reason = "No material factual change versus last Truth Epoch narrative snapshot."
        elif language_violations:
            silence_reason = "Narrative blocked by language policy violation."
        elif gating_reasons:
            silence_reason = gating_reasons[0]["detail"]
        else:
            silence_reason = "Narrative gated by governance constraints."

    references = _collect_provenance_refs(market, suppression_registry)
    gating_reason = gating_reasons[0]["detail"] if gating_reasons else "No active narrative gating reason."

    payload = {
        "market": market,
        "computed_at": now,
        "truth_epoch": truth_epoch,
        "narrative_mode": mode,
        "posture": _posture_for_mode(mode),
        "tone": _tone_for_mode(mode),
        "summary": summary,
        "silence_reason": silence_reason,
        "gating_reason": gating_reason,
        "gating_reasons": gating_reasons,
        "regime_state": regime_state,
        "regime_confidence": regime_confidence,
        "regime_reason": regime_reason,
        "canonical_state": canonical_state,
        "suppression_state": suppression_code,
        "provenance_references": references,
        "citations": references,
        "language_policy": {
            "violations": language_violations,
            "violations_count": len(language_violations),
            "banned_terms_count": len(BANNED_TERMS),
        },
        "narrative_diff": {
            "status": diff_status,
            "changed_fields": changed_fields,
            "baseline_truth_epoch": previous_epoch or None,
            "baseline_artifact": str(state_path.relative_to(PROJECT_ROOT)),
        },
        "material_facts_hash": material_facts_hash,
        "material_facts": material_facts,
        "version": "1.0.0-F3",
    }

    _write_json(state_path, payload)

    if mode != "EXPLANATORY":
        _append_jsonl(
            AUDIT_DIR / "narrative_suppressions.jsonl",
            {
                "event": "NARRATIVE_SUPPRESSED",
                "computed_at": now,
                "market": market,
                "truth_epoch": truth_epoch,
                "narrative_mode": mode,
                "suppression_state": suppression_code,
                "canonical_state": canonical_state,
                "regime_state": regime_state,
                "gating_reason_codes": [r.get("code") for r in gating_reasons],
                "gating_reason": gating_reason,
                "artifact": str(state_path.relative_to(PROJECT_ROOT)),
            },
        )

    if previous_mode != mode:
        _append_jsonl(
            AUDIT_DIR / "narrative_mode_transitions.jsonl",
            {
                "event": "NARRATIVE_MODE_TRANSITION",
                "computed_at": now,
                "market": market,
                "truth_epoch": truth_epoch,
                "from_mode": previous_mode,
                "to_mode": mode,
                "diff_status": diff_status,
                "gating_reason": gating_reason,
                "artifact": str(state_path.relative_to(PROJECT_ROOT)),
            },
        )

    return {
        "narrative": payload,
        "suppression": suppression_state,
        "suppression_registry": suppression_registry,
    }


def compute_narrative_for_markets(markets: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    target = markets or ["US", "INDIA"]
    result: Dict[str, Dict[str, Any]] = {}
    for market in target:
        result[market.upper()] = compute_narrative_for_market(market)
    return result
