from typing import Dict, Any, List

from dashboard.backend.loaders.suppression import load_suppression_status

try:
    from governance.narrative_guard import compute_narrative_for_market
except Exception:
    from src.governance.narrative_guard import compute_narrative_for_market  # type: ignore


def load_system_narrative(market: str = "US") -> Dict[str, Any]:
    """
    Returns F3-governed narrative payload with explicit narrative_mode, gating
    reasons, and provenance references.
    """
    market = market.upper()
    payload = compute_narrative_for_market(market)
    return payload.get("narrative", {})


def load_system_blockers(market: str = "US") -> List[Dict[str, Any]]:
    """
    Returns explicit suppression blockers for the 'Why Nothing Is Happening' panel.
    """
    market = market.upper()
    payload = load_suppression_status(market)
    suppression = payload.get("suppression", {})
    reasons = payload.get("registry", {}).get("reasons", []) or []
    state = suppression.get("suppression_state", "NONE")

    if state == "NONE":
        return [
            {
                "id": "suppression_none",
                "label": "Suppression State",
                "passed": True,
                "reason": "No active suppression state registered.",
            }
        ]

    blockers: List[Dict[str, Any]] = []
    for reason in reasons:
        blockers.append(
            {
                "id": reason.get("reason_id", "UNKNOWN"),
                "label": f"{reason.get('suppression_state', 'UNKNOWN')} ({reason.get('blocking_layer', 'UNKNOWN')})",
                "passed": False,
                "reason": (
                    f"ACTION BLOCKED DUE TO: {reason.get('blocking_condition', 'No condition provided.')} "
                    f"Clearing condition: {reason.get('clearing_condition', 'Resolve blocker.')}"
                ),
                "since_timestamp": reason.get("since_timestamp"),
                "affected_actions": reason.get("affected_actions", []),
            }
        )
    return blockers
