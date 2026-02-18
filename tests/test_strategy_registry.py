import pytest

from src.layers.strategy_registry import StrategyRegistry, get_strategy_health
from src.models.meta_models import RegimeState
from src.models.strategy_models import ConvergenceResult, StrategyTemplate


def _regime(name: str) -> RegimeState:
    return RegimeState(regime=name, volatility=0.30)  # type: ignore[arg-type]


def _convergence(
    *,
    score: float = 0.80,
    lens_count: int = 4,
    direction: str = "LONG",
    status: str = "VALID",
    symbol: str = "AAPL",
) -> ConvergenceResult:
    return ConvergenceResult(
        symbol=symbol,
        direction=direction,  # type: ignore[arg-type]
        convergence_score=score,
        lens_count=lens_count,
        status=status,
    )


def _rejection_map(decision) -> dict:
    return {item.strategy_id: item.rejection_reason for item in decision.rejected_strategies}


def test_regime_block_trending_blocks_mean_reversion():
    decision = StrategyRegistry().select_strategy(
        _convergence(score=0.90, lens_count=4, direction="LONG"),
        _regime("TRENDING"),
    )
    assert _rejection_map(decision)["MEAN_REVERSION"] == "Regime incompatible"


def test_threshold_boundary_for_breakout():
    registry = StrategyRegistry()

    at_threshold = registry.select_strategy(
        _convergence(score=0.75, lens_count=4, direction="LONG"),
        _regime("TRENDING"),
    )
    below_threshold = registry.select_strategy(
        _convergence(score=0.74, lens_count=4, direction="LONG"),
        _regime("TRENDING"),
    )

    assert at_threshold.selected_strategy == "BREAKOUT"
    assert _rejection_map(below_threshold)["BREAKOUT"] == "Score below threshold"


def test_lens_count_gate_for_breakout():
    registry = StrategyRegistry()

    low_lens = registry.select_strategy(
        _convergence(score=0.90, lens_count=3, direction="LONG"),
        _regime("TRENDING"),
    )
    exact_lens = registry.select_strategy(
        _convergence(score=0.90, lens_count=4, direction="LONG"),
        _regime("TRENDING"),
    )

    assert _rejection_map(low_lens)["BREAKOUT"] == "Lens count insufficient"
    assert "BREAKOUT" in exact_lens.candidate_strategies


def test_direction_permission_short_breakout_rejected():
    decision = StrategyRegistry().select_strategy(
        _convergence(score=0.90, lens_count=4, direction="SHORT"),
        _regime("TRENDING"),
    )
    assert _rejection_map(decision)["BREAKOUT"] == "Direction not allowed"


def test_multi_strategy_ranking_is_deterministic():
    custom_templates = (
        StrategyTemplate(
            strategy_id="TREND_FOLLOW",
            compatible_regimes=("TRENDING",),
            min_score_threshold=0.70,
            min_lens_count=3,
            allowed_directions=("LONG", "SHORT"),
            risk_profile="MODERATE",
            time_horizon="POSITIONAL",
        ),
        StrategyTemplate(
            strategy_id="SWING",
            compatible_regimes=("TRENDING",),
            min_score_threshold=0.70,
            min_lens_count=4,
            allowed_directions=("LONG", "SHORT"),
            risk_profile="MODERATE",
            time_horizon="SWING",
        ),
        StrategyTemplate(
            strategy_id="PULLBACK",
            compatible_regimes=("TRENDING", "TRANSITION"),
            min_score_threshold=0.70,
            min_lens_count=5,
            allowed_directions=("LONG", "SHORT"),
            risk_profile="MODERATE",
            time_horizon="SWING",
        ),
    )
    registry = StrategyRegistry(strategy_templates=custom_templates)

    decision = registry.select_strategy(
        _convergence(score=0.80, lens_count=5, direction="LONG"),
        _regime("TRENDING"),
    )

    assert decision.candidate_strategies == ("SWING", "TREND_FOLLOW", "PULLBACK")
    assert decision.selected_strategy == "SWING"


def test_no_strategy_case_low_score():
    decision = StrategyRegistry().select_strategy(
        _convergence(score=0.49, lens_count=5, direction="LONG"),
        _regime("TRENDING"),
    )
    assert decision.selected_strategy == "NONE"
    assert decision.status == "NO_VALID_STRATEGY"


def test_all_regime_incompatible_returns_strategy_regime_blocked():
    decision = StrategyRegistry().select_strategy(
        _convergence(score=0.90, lens_count=5, direction="LONG"),
        _regime("UNSUPPORTED"),
    )
    assert decision.selected_strategy == "NONE"
    assert decision.status == "STRATEGY_REGIME_BLOCKED"
    assert all(item.rejection_reason == "Regime incompatible" for item in decision.rejected_strategies)


def test_deterministic_replay_same_output_10_runs():
    registry = StrategyRegistry()
    results = [
        registry.select_strategy(
            _convergence(score=0.80, lens_count=4, direction="LONG"),
            _regime("TRENDING"),
        )
        for _ in range(10)
    ]

    fingerprints = [
        (
            item.selected_strategy,
            item.candidate_strategies,
            tuple((rej.strategy_id, rej.rejection_reason) for rej in item.rejected_strategies),
            item.status,
            item.input_hash,
        )
        for item in results
    ]
    assert len(set(fingerprints)) == 1

    scores = [item.convergence_score for item in results]
    assert max(scores) - min(scores) < 0.01


def test_explainability_coverage_for_all_rejection_reasons():
    custom_templates = (
        StrategyTemplate(
            strategy_id="BREAKOUT",
            compatible_regimes=("CHOP",),
            min_score_threshold=0.70,
            min_lens_count=3,
            allowed_directions=("LONG",),
            risk_profile="AGGRESSIVE",
            time_horizon="SWING",
        ),
        StrategyTemplate(
            strategy_id="PULLBACK",
            compatible_regimes=("TRENDING",),
            min_score_threshold=0.90,
            min_lens_count=3,
            allowed_directions=("LONG",),
            risk_profile="MODERATE",
            time_horizon="SWING",
        ),
        StrategyTemplate(
            strategy_id="SCALP",
            compatible_regimes=("TRENDING",),
            min_score_threshold=0.70,
            min_lens_count=5,
            allowed_directions=("LONG",),
            risk_profile="AGGRESSIVE",
            time_horizon="INTRADAY",
        ),
        StrategyTemplate(
            strategy_id="SWING",
            compatible_regimes=("TRENDING",),
            min_score_threshold=0.70,
            min_lens_count=3,
            allowed_directions=("SHORT",),
            risk_profile="MODERATE",
            time_horizon="SWING",
        ),
    )
    registry = StrategyRegistry(strategy_templates=custom_templates)
    decision = registry.select_strategy(
        _convergence(score=0.80, lens_count=4, direction="LONG"),
        _regime("TRENDING"),
    )

    allowed_reasons = {
        "Score below threshold",
        "Lens count insufficient",
        "Regime incompatible",
        "Direction not allowed",
    }
    reasons = {item.rejection_reason for item in decision.rejected_strategies}
    assert reasons == allowed_reasons
    for rejected in decision.rejected_strategies:
        assert rejected.rejection_reason in allowed_reasons


def test_invalid_convergence_status_returns_no_valid_strategy():
    decision = StrategyRegistry().select_strategy(
        _convergence(score=0.80, lens_count=4, direction="LONG", status="INVALID"),
        _regime("TRENDING"),
    )
    assert decision.selected_strategy == "NONE"
    assert decision.status == "NO_VALID_STRATEGY"


def test_latency_guard_sets_latency_violation(monkeypatch):
    timeline = iter([10.0, 10.6])
    monkeypatch.setattr("src.layers.strategy_registry.time.perf_counter", lambda: next(timeline))

    decision = StrategyRegistry().select_strategy(
        _convergence(score=0.80, lens_count=4, direction="LONG"),
        _regime("TRENDING"),
    )
    assert decision.status == "LATENCY_VIOLATION"
    assert decision.selected_strategy == "NONE"


def test_strategy_health_hook():
    health = get_strategy_health()
    assert health["regime_enforced"] is True
    assert health["threshold_enforced"] is True
    assert health["deterministic"] is True


def test_latency_within_range_in_normal_operation():
    decision = StrategyRegistry().select_strategy(
        _convergence(score=0.80, lens_count=4, direction="LONG"),
        _regime("TRENDING"),
    )
    assert decision.latency_ms > 0.0
    assert decision.latency_ms < 500.0
