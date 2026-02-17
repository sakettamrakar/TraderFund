"""
Post-merge semantic regression detector.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


def detect_regression(
    pre_score: float,
    post_score: float,
    tolerance: float = 0.03,
    pre_report: Optional[Dict[str, Any]] = None,
    post_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Detect semantic regression based on score drop and drift escalation.
    """
    pre = pre_report or {}
    post = post_report or {}

    pre_score_f = float(pre_score)
    post_score_f = float(post_score)
    tolerance_f = float(tolerance)

    reasons = []

    # Rule 1: score regression with tolerance.
    if post_score_f < (pre_score_f - tolerance_f):
        reasons.append(
            f"Post score dropped beyond tolerance: {post_score_f:.4f} < "
            f"{pre_score_f:.4f} - {tolerance_f:.4f}"
        )

    # Rule 2: drift signal increase.
    pre_drift_flags = _drift_signal_count(pre)
    post_drift_flags = _drift_signal_count(post)
    if post_drift_flags > pre_drift_flags:
        reasons.append(
            f"Drift flags increased: pre={pre_drift_flags}, post={post_drift_flags}"
        )

    # Rule 3: overreach appears post-merge.
    pre_overreach = _overreach_detected(pre)
    post_overreach = _overreach_detected(post)
    if post_overreach and not pre_overreach:
        reasons.append("Overreach detected post-merge.")

    regression = bool(reasons)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regression": regression,
        "pre_score": round(pre_score_f, 6),
        "post_score": round(post_score_f, 6),
        "tolerance": round(tolerance_f, 6),
        "score_delta": round(post_score_f - pre_score_f, 6),
        "pre_drift_flags": pre_drift_flags,
        "post_drift_flags": post_drift_flags,
        "pre_overreach": pre_overreach,
        "post_overreach": post_overreach,
        "reasons": reasons,
    }


def _drift_signal_count(report: Dict[str, Any]) -> int:
    drift = report.get("drift", {})
    if not isinstance(drift, dict):
        drift = {}

    count = 0
    if drift.get("overreach_detected"):
        count += 1
    for key in ("missing_requirements", "unintended_modifications", "semantic_mismatch"):
        value = drift.get(key, [])
        if isinstance(value, list):
            count += len(value)
    return count


def _overreach_detected(report: Dict[str, Any]) -> bool:
    drift = report.get("drift", {})
    return bool(isinstance(drift, dict) and drift.get("overreach_detected"))
