"""
F5 Suppression State Orchestrator.

Computes explicit, enumerable suppression state per market and persists:
- suppression state artifact
- suppression reason registry artifact
- transition audit log

Safety invariants:
- Read-only interpretation of governance/intelligence artifacts.
- No execution/capital mutation.
- No TE advancement.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
INTEL_DIR = PROJECT_ROOT / "docs" / "intelligence"
TEMPORAL_DIR = INTEL_DIR / "temporal"
AUDIT_DIR = PROJECT_ROOT / "docs" / "audit" / "f5_suppression"

SUPPRESSION_STATES = [
    "NONE",
    "POLICY_BLOCKED",
    "REGIME_DEGRADED",
    "DATA_PARTIAL",
    "TEMPORAL_DRIFT",
    "FRAGILITY_CONSTRAINT",
    "MULTI_CAUSAL",
]

REASON_PRIORITY = {
    "R-TEMPORAL-DRIFT": 1,
    "R-DATA-PARTIAL": 2,
    "R-REGIME-DEGRADED": 3,
    "R-POLICY-BLOCKED": 4,
    "R-FRAGILITY-CONSTRAINT": 5,
}

ALL_ACTIONS = [
    "ALLOW_LONG_ENTRY",
    "ALLOW_SHORT_ENTRY",
    "ALLOW_POSITION_HOLD",
    "ALLOW_REBALANCING",
    "ALLOW_LONG_ENTRY_SPECIAL",
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


def _reason(
    reason_id: str,
    suppression_state: str,
    blocking_layer: str,
    blocking_condition: str,
    affected_actions: List[str],
    clearing_condition: str,
    source_artifacts: List[str],
) -> Dict[str, Any]:
    return {
        "reason_id": reason_id,
        "suppression_state": suppression_state,
        "blocking_layer": blocking_layer,
        "blocking_condition": blocking_condition,
        "affected_actions": sorted(set(affected_actions)),
        "clearing_condition": clearing_condition,
        "source_artifacts": source_artifacts,
    }


def _load_truth_epoch(market: str) -> str:
    # F1 temporal state is the preferred epoch source after F1 remediation.
    temporal = _read_json(TEMPORAL_DIR / f"temporal_state_{market}.json")
    te = (
        temporal.get("temporal_state", {})
        .get("truth_epoch", {})
        .get("epoch_id")
    )
    if te:
        return str(te)
    te_ts = (
        temporal.get("temporal_state", {})
        .get("truth_epoch", {})
        .get("timestamp")
    )
    if te_ts:
        return f"TE-{str(te_ts)}"
    return "TE-2026-01-30"


def _affected_actions_from_policy(policy: Dict[str, Any]) -> List[str]:
    blocked = set(policy.get("blocked_actions", []) or [])
    permissions = set(policy.get("permissions", []) or [])
    if permissions == {"OBSERVE_ONLY"}:
        blocked.update(ALL_ACTIONS)
    else:
        blocked.update([a for a in ALL_ACTIONS if a not in permissions])
    return sorted(blocked)


def _reason_key(reason: Dict[str, Any]) -> str:
    return f"{reason.get('reason_id')}::{reason.get('blocking_condition')}"


def _parse_previous_reason_since(previous_registry: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for item in previous_registry.get("reasons", []) or []:
        key = _reason_key(item)
        since = item.get("since_timestamp")
        if key and since:
            out[key] = since
    return out


def _derive_reasons_for_market(market: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    market = market.upper()
    temporal = _read_json(TEMPORAL_DIR / f"temporal_state_{market}.json")
    partiality = _read_json(INTEL_DIR / f"canonical_partiality_state_{market}.json")
    policy = _read_json(INTEL_DIR / f"decision_policy_{market}.json").get("policy_decision", {})
    fragility = _read_json(INTEL_DIR / f"fragility_context_{market}.json").get("fragility_context", {})
    regime_ctx = _read_json(PROJECT_ROOT / "docs" / "evolution" / "context" / f"regime_context_{market}.json").get("regime_context", {})

    reasons: List[Dict[str, Any]] = []

    drift = temporal.get("drift_status", {})
    holds = temporal.get("holds", {})
    drift_days = int(drift.get("evaluation_drift_days", 0) or 0)
    drift_code = str(drift.get("status_code", "UNKNOWN"))
    if drift_days > 0 or holds.get("evaluation_hold") is True:
        reasons.append(
            _reason(
                reason_id="R-TEMPORAL-DRIFT",
                suppression_state="TEMPORAL_DRIFT",
                blocking_layer="GOVERNANCE",
                blocking_condition=drift.get("message") or f"Temporal hold active ({drift_code}).",
                affected_actions=ALL_ACTIONS,
                clearing_condition=(
                    "Resolve temporal hold by satisfying bounded drift requirements and completing "
                    "operator-mediated catch-up evaluation windows without advancing Truth Epoch automatically."
                ),
                source_artifacts=[f"docs/intelligence/temporal/temporal_state_{market}.json"],
            )
        )

    canonical_state = str(partiality.get("canonical_state", "UNKNOWN"))
    missing_roles = partiality.get("missing_roles", []) or []
    stale_roles = partiality.get("stale_roles", []) or []
    if canonical_state in {"CANONICAL_PARTIAL", "CANONICAL_MIXED"}:
        reasons.append(
            _reason(
                reason_id="R-DATA-PARTIAL",
                suppression_state="DATA_PARTIAL",
                blocking_layer="DATA",
                blocking_condition=(
                    f"Canonical state {canonical_state}. Missing roles: {missing_roles or ['NONE']}. "
                    f"Stale roles: {stale_roles or ['NONE']}."
                ),
                affected_actions=ALL_ACTIONS,
                clearing_condition=(
                    "Restore canonical completeness and freshness alignment for required roles "
                    "before allowing regime or policy expansion."
                ),
                source_artifacts=[f"docs/intelligence/canonical_partiality_state_{market}.json"],
            )
        )

    regime_state = str(policy.get("regime_state", regime_ctx.get("regime_code", "UNKNOWN")))
    regime_conf = str(policy.get("regime_confidence", regime_ctx.get("regime_confidence", "UNKNOWN")))
    regime_reason = str(policy.get("regime_reason", regime_ctx.get("regime_reason", "Regime unavailable.")))
    if regime_state == "UNKNOWN" and regime_conf.upper() == "DEGRADED":
        reasons.append(
            _reason(
                reason_id="R-REGIME-DEGRADED",
                suppression_state="REGIME_DEGRADED",
                blocking_layer="INTELLIGENCE",
                blocking_condition=f"Regime degraded to UNKNOWN. {regime_reason}",
                affected_actions=ALL_ACTIONS,
                clearing_condition="Regime must be recomputed on canonical-complete inputs and declared non-degraded.",
                source_artifacts=[
                    f"docs/intelligence/decision_policy_{market}.json",
                    f"docs/evolution/context/regime_context_{market}.json",
                ],
            )
        )

    policy_state = str(policy.get("policy_state", "OFFLINE")).upper()
    policy_permissions = policy.get("permissions", []) or []
    policy_blocked = policy_state in {"HALTED", "RESTRICTED", "OFFLINE"} or policy_permissions == ["OBSERVE_ONLY"]
    if policy_blocked:
        reasons.append(
            _reason(
                reason_id="R-POLICY-BLOCKED",
                suppression_state="POLICY_BLOCKED",
                blocking_layer="INTELLIGENCE",
                blocking_condition=str(policy.get("reason", f"Policy state is {policy_state}.")),
                affected_actions=_affected_actions_from_policy(policy),
                clearing_condition=(
                    "Policy must evaluate with non-observe-only permissions under declared TE scope "
                    "while preserving no-execution invariants."
                ),
                source_artifacts=[f"docs/intelligence/decision_policy_{market}.json"],
            )
        )

    frag_constraints = fragility.get("constraints_applied", []) or []
    final_intents = fragility.get("final_authorized_intents", []) or []
    stress_state = str(fragility.get("stress_state", "UNKNOWN")).upper()
    fragility_blocked = bool(frag_constraints) or (final_intents == ["OBSERVE_ONLY"] and stress_state != "NORMAL")
    if fragility_blocked:
        reasons.append(
            _reason(
                reason_id="R-FRAGILITY-CONSTRAINT",
                suppression_state="FRAGILITY_CONSTRAINT",
                blocking_layer="INTELLIGENCE",
                blocking_condition=str(fragility.get("reason", f"Fragility constraints active ({stress_state}).")),
                affected_actions=list(frag_constraints) or ALL_ACTIONS,
                clearing_condition="Fragility constraints must be removed with stress posture explicitly normalized.",
                source_artifacts=[f"docs/intelligence/fragility_context_{market}.json"],
            )
        )

    evidence = {
        "temporal": temporal,
        "partiality": partiality,
        "policy": policy,
        "fragility": fragility,
        "regime_context": regime_ctx,
    }
    return reasons, evidence


def compute_suppression_for_market(market: str) -> Dict[str, Any]:
    market = market.upper()
    now = _utc_now_iso()
    truth_epoch = _load_truth_epoch(market)
    reasons, evidence = _derive_reasons_for_market(market)

    previous_state_path = INTEL_DIR / f"suppression_state_{market}.json"
    previous_registry_path = INTEL_DIR / f"suppression_reason_registry_{market}.json"
    previous_state = _read_json(previous_state_path)
    previous_registry = _read_json(previous_registry_path)
    previous_since = _parse_previous_reason_since(previous_registry)

    for item in reasons:
        key = _reason_key(item)
        item["since_timestamp"] = previous_since.get(key, now)

    if not reasons:
        suppression_state = "NONE"
    elif len(reasons) > 1:
        suppression_state = "MULTI_CAUSAL"
    else:
        suppression_state = reasons[0].get("suppression_state", "MULTI_CAUSAL")

    reasons_sorted = sorted(
        reasons,
        key=lambda r: (
            REASON_PRIORITY.get(str(r.get("reason_id", "")), 99),
            str(r.get("reason_id", "")),
        ),
    )
    primary_reason = reasons_sorted[0] if reasons_sorted else None
    secondary_reasons = reasons_sorted[1:] if len(reasons_sorted) > 1 else []

    affected_actions = sorted({action for r in reasons_sorted for action in (r.get("affected_actions", []) or [])})
    since_timestamp = None
    if reasons_sorted:
        since_timestamp = sorted([r.get("since_timestamp") for r in reasons_sorted if r.get("since_timestamp")])[0]

    summary = {
        "market": market,
        "truth_epoch": truth_epoch,
        "computed_at": now,
        "suppression_state": suppression_state,
        "since_timestamp": since_timestamp,
        "affected_actions": affected_actions,
        "primary_reason": primary_reason,
        "secondary_reasons": secondary_reasons,
        "clearance_statement": (
            "ACTION UNBLOCKING REQUIRES ALL ACTIVE SUPPRESSION REASONS TO CLEAR. "
            "No automatic execution or truth advancement is permitted."
        ),
        "version": "1.0.0-F5",
    }

    registry = {
        "market": market,
        "truth_epoch": truth_epoch,
        "computed_at": now,
        "suppression_state": suppression_state,
        "reasons": reasons_sorted,
        "reason_count": len(reasons_sorted),
        "version": "1.0.0-F5",
    }

    _write_json(previous_state_path, summary)
    _write_json(previous_registry_path, registry)

    previous_signature = {
        "suppression_state": previous_state.get("suppression_state"),
        "reason_ids": sorted({str(r.get("reason_id")) for r in previous_registry.get("reasons", []) or [] if r.get("reason_id")}),
        "conditions": sorted({str(r.get("blocking_condition")) for r in previous_registry.get("reasons", []) or [] if r.get("blocking_condition")}),
    }
    current_signature = {
        "suppression_state": suppression_state,
        "reason_ids": sorted({str(r.get("reason_id")) for r in reasons_sorted if r.get("reason_id")}),
        "conditions": sorted({str(r.get("blocking_condition")) for r in reasons_sorted if r.get("blocking_condition")}),
    }

    _append_jsonl(
        AUDIT_DIR / "suppression_state_snapshots.jsonl",
        {
            "event": "SUPPRESSION_STATE_SNAPSHOT",
            "computed_at": now,
            "market": market,
            "truth_epoch": truth_epoch,
            "suppression_state": suppression_state,
            "reason_count": len(reasons_sorted),
            "primary_reason_id": primary_reason.get("reason_id") if primary_reason else None,
            "artifact": str(previous_state_path.relative_to(PROJECT_ROOT)),
        },
    )

    if previous_signature != current_signature:
        _append_jsonl(
            AUDIT_DIR / "suppression_state_transitions.jsonl",
            {
                "event": "SUPPRESSION_STATE_CHANGED",
                "computed_at": now,
                "market": market,
                "truth_epoch": truth_epoch,
                "from_state": previous_signature.get("suppression_state"),
                "to_state": suppression_state,
                "from_reason_ids": previous_signature.get("reason_ids", []),
                "to_reason_ids": current_signature.get("reason_ids", []),
                "from_conditions": previous_signature.get("conditions", []),
                "to_conditions": current_signature.get("conditions", []),
            },
        )

    return {
        "summary": summary,
        "registry": registry,
        "evidence": evidence,
    }


def compute_suppression_for_markets(markets: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    target = markets or ["US", "INDIA"]
    out: Dict[str, Dict[str, Any]] = {}
    for market in target:
        out[market.upper()] = compute_suppression_for_market(market)
    return out
