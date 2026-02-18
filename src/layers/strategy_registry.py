"""
L7 Strategy Registry: deterministic policy-based strategy selector.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Sequence, Tuple

from src.models.meta_models import RegimeState
from src.models.strategy_models import (
    ConvergenceResult,
    StrategyDecision,
    StrategyRejection,
    StrategyTemplate,
)

_VALID_CONVERGENCE_STATUS = "VALID"
_GLOBAL_MIN_SCORE = 0.50
_LATENCY_LIMIT_MS = 500.0
_NO_STRATEGY = "NONE"

DEFAULT_STRATEGY_TEMPLATES: Tuple[StrategyTemplate, ...] = (
    StrategyTemplate(
        strategy_id="BREAKOUT",
        compatible_regimes=("TRENDING",),
        min_score_threshold=0.75,
        min_lens_count=4,
        allowed_directions=("LONG",),
        risk_profile="AGGRESSIVE",
        time_horizon="SWING",
    ),
    StrategyTemplate(
        strategy_id="PULLBACK",
        compatible_regimes=("TRENDING", "TRANSITION"),
        min_score_threshold=0.65,
        min_lens_count=3,
        allowed_directions=("LONG", "SHORT"),
        risk_profile="MODERATE",
        time_horizon="SWING",
    ),
    StrategyTemplate(
        strategy_id="MEAN_REVERSION",
        compatible_regimes=("CHOP", "TRANSITION"),
        min_score_threshold=0.60,
        min_lens_count=3,
        allowed_directions=("LONG", "SHORT"),
        risk_profile="MODERATE",
        time_horizon="SHORT_TERM",
    ),
    StrategyTemplate(
        strategy_id="TREND_FOLLOW",
        compatible_regimes=("TRENDING",),
        min_score_threshold=0.72,
        min_lens_count=3,
        allowed_directions=("LONG", "SHORT"),
        risk_profile="MODERATE",
        time_horizon="POSITIONAL",
    ),
    StrategyTemplate(
        strategy_id="VOLATILITY_EXPANSION",
        compatible_regimes=("STRESS",),
        min_score_threshold=0.70,
        min_lens_count=3,
        allowed_directions=("LONG", "SHORT"),
        risk_profile="AGGRESSIVE",
        time_horizon="SWING",
    ),
    StrategyTemplate(
        strategy_id="SCALP",
        compatible_regimes=("CHOP", "VOLATILE"),
        min_score_threshold=0.62,
        min_lens_count=3,
        allowed_directions=("LONG", "SHORT"),
        risk_profile="AGGRESSIVE",
        time_horizon="INTRADAY",
    ),
    StrategyTemplate(
        strategy_id="SWING",
        compatible_regimes=("TRENDING", "TRANSITION", "VOLATILE"),
        min_score_threshold=0.66,
        min_lens_count=3,
        allowed_directions=("LONG", "SHORT"),
        risk_profile="MODERATE",
        time_horizon="SWING",
    ),
    StrategyTemplate(
        strategy_id="POSITIONAL",
        compatible_regimes=("TRENDING", "ACCUMULATION", "DISTRIBUTION"),
        min_score_threshold=0.64,
        min_lens_count=2,
        allowed_directions=("LONG",),
        risk_profile="CONSERVATIVE",
        time_horizon="POSITIONAL",
    ),
)


class StrategyRegistry:
    def __init__(self, strategy_templates: Sequence[StrategyTemplate] | None = None) -> None:
        templates = tuple(strategy_templates) if strategy_templates is not None else DEFAULT_STRATEGY_TEMPLATES
        if not templates:
            raise ValueError("Strategy registry requires at least one strategy template")

        self._strategy_templates = tuple(sorted(templates, key=lambda item: item.strategy_id))
        self._assert_unique_strategy_ids(self._strategy_templates)
        self._catalog_signature = tuple(
            (
                item.strategy_id,
                item.compatible_regimes,
                item.min_score_threshold,
                item.min_lens_count,
                item.allowed_directions,
            )
            for item in self._strategy_templates
        )

    def select_strategy(self, convergence: ConvergenceResult, regime_state: RegimeState) -> StrategyDecision:
        start = time.perf_counter()
        symbol = str(getattr(convergence, "symbol", ""))
        direction = str(getattr(convergence, "direction", "")).upper()
        regime = str(getattr(regime_state, "regime", "UNKNOWN")).upper()
        convergence_score = self._to_float(getattr(convergence, "convergence_score", 0.0))
        lens_count = self._to_int(getattr(convergence, "lens_count", 0))
        convergence_status = str(getattr(convergence, "status", "INVALID")).upper()
        input_hash = self.compute_input_hash(convergence, regime_state)

        if convergence_status != _VALID_CONVERGENCE_STATUS:
            return self._build_decision(
                start=start,
                symbol=symbol,
                direction=direction,
                selected_strategy=_NO_STRATEGY,
                candidate_strategies=tuple(),
                rejected_strategies=tuple(),
                selection_reason="Convergence status is not VALID",
                regime=regime,
                convergence_score=convergence_score,
                input_hash=input_hash,
                status="NO_VALID_STRATEGY",
            )

        if convergence_score < _GLOBAL_MIN_SCORE:
            return self._build_decision(
                start=start,
                symbol=symbol,
                direction=direction,
                selected_strategy=_NO_STRATEGY,
                candidate_strategies=tuple(),
                rejected_strategies=tuple(),
                selection_reason=f"Convergence score below floor ({_GLOBAL_MIN_SCORE:.2f})",
                regime=regime,
                convergence_score=convergence_score,
                input_hash=input_hash,
                status="NO_VALID_STRATEGY",
            )

        candidate_templates = []
        rejected = []

        for template in self._strategy_templates:
            reason = self._evaluate_template(
                template=template,
                regime=regime,
                direction=direction,
                convergence_score=convergence_score,
                lens_count=lens_count,
            )
            if reason is None:
                candidate_templates.append(template)
            else:
                rejected.append(StrategyRejection(strategy_id=template.strategy_id, rejection_reason=reason))

        ranked_templates = self._rank_candidates(tuple(candidate_templates))
        candidate_ids = tuple(template.strategy_id for template in ranked_templates)
        rejected_tuple = tuple(rejected)

        if not ranked_templates:
            all_regime_blocked = bool(rejected_tuple) and all(
                item.rejection_reason == "Regime incompatible" for item in rejected_tuple
            )
            status = "STRATEGY_REGIME_BLOCKED" if all_regime_blocked else "NO_VALID_STRATEGY"
            reason = (
                "No strategy compatible with current regime"
                if all_regime_blocked
                else "No strategy passed deterministic policy gates"
            )
            return self._build_decision(
                start=start,
                symbol=symbol,
                direction=direction,
                selected_strategy=_NO_STRATEGY,
                candidate_strategies=candidate_ids,
                rejected_strategies=rejected_tuple,
                selection_reason=reason,
                regime=regime,
                convergence_score=convergence_score,
                input_hash=input_hash,
                status=status,
            )

        selected = ranked_templates[0].strategy_id
        return self._build_decision(
            start=start,
            symbol=symbol,
            direction=direction,
            selected_strategy=selected,
            candidate_strategies=candidate_ids,
            rejected_strategies=rejected_tuple,
            selection_reason=(
                f"Selected {selected} via deterministic ranking "
                "(threshold, regime specificity, lens requirement)"
            ),
            regime=regime,
            convergence_score=convergence_score,
            input_hash=input_hash,
            status="VALID_STRATEGY_SELECTED",
        )

    def compute_input_hash(self, convergence: ConvergenceResult, regime_state: RegimeState) -> str:
        payload = json.dumps(
            {
                "symbol": str(getattr(convergence, "symbol", "")),
                "direction": str(getattr(convergence, "direction", "")).upper(),
                "convergence_score": self._to_float(getattr(convergence, "convergence_score", 0.0)),
                "lens_count": self._to_int(getattr(convergence, "lens_count", 0)),
                "convergence_status": str(getattr(convergence, "status", "INVALID")).upper(),
                "regime": str(getattr(regime_state, "regime", "UNKNOWN")).upper(),
                "catalog_signature": self._catalog_signature,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _assert_unique_strategy_ids(templates: Tuple[StrategyTemplate, ...]) -> None:
        seen = set()
        for template in templates:
            if template.strategy_id in seen:
                raise ValueError(f"Duplicate strategy_id found: {template.strategy_id}")
            seen.add(template.strategy_id)

    @staticmethod
    def _evaluate_template(
        template: StrategyTemplate,
        regime: str,
        direction: str,
        convergence_score: float,
        lens_count: int,
    ) -> str | None:
        if regime not in template.compatible_regimes:
            return "Regime incompatible"
        if convergence_score < template.min_score_threshold:
            return "Score below threshold"
        if lens_count < template.min_lens_count:
            return "Lens count insufficient"
        if direction not in template.allowed_directions:
            return "Direction not allowed"
        return None

    @staticmethod
    def _rank_candidates(candidates: Tuple[StrategyTemplate, ...]) -> Tuple[StrategyTemplate, ...]:
        return tuple(
            sorted(
                candidates,
                key=lambda item: (
                    -item.min_score_threshold,
                    len(item.compatible_regimes),
                    -item.min_lens_count,
                    item.strategy_id,
                ),
            )
        )

    @staticmethod
    def _to_float(value: object) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _to_int(value: object) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _build_decision(
        self,
        *,
        start: float,
        symbol: str,
        direction: str,
        selected_strategy: str,
        candidate_strategies: Tuple[str, ...],
        rejected_strategies: Tuple[StrategyRejection, ...],
        selection_reason: str,
        regime: str,
        convergence_score: float,
        input_hash: str,
        status: str,
    ) -> StrategyDecision:
        latency_ms = (time.perf_counter() - start) * 1000.0
        final_status = status
        final_selected = selected_strategy
        final_reason = selection_reason

        if latency_ms <= 0.0 or latency_ms >= _LATENCY_LIMIT_MS:
            final_status = "LATENCY_VIOLATION"
            final_selected = _NO_STRATEGY
            final_reason = f"Latency guard violated ({latency_ms:.3f}ms)"

        return StrategyDecision(
            symbol=symbol,
            direction=direction,
            selected_strategy=final_selected,
            candidate_strategies=candidate_strategies,
            rejected_strategies=rejected_strategies,
            selection_reason=final_reason,
            regime=regime,
            convergence_score=convergence_score,
            latency_ms=latency_ms,
            input_hash=input_hash,
            status=final_status,
        )

    def get_strategy_health(self) -> dict:
        return {
            "regime_enforced": True,
            "threshold_enforced": True,
            "deterministic": True,
        }


def get_strategy_health() -> dict:
    return StrategyRegistry().get_strategy_health()
