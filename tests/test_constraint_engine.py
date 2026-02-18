import pytest
import time
from src.models.constraint_models import StrategyDecision, PortfolioState, RiskConfig, ConstraintDecision
from src.layers.constraint_engine import ConstraintEngine

@pytest.fixture
def engine():
    return ConstraintEngine()

@pytest.fixture
def default_config():
    return RiskConfig(
        max_position_pct=0.05,
        max_sector_exposure_pct=0.25,
        max_gross_exposure_pct=1.0,
        max_net_exposure_pct=0.5,
        max_drawdown_pct=0.10,
        stress_scaling_factor=0.5,
        transition_scaling_factor=0.75
    )

@pytest.fixture
def default_portfolio():
    return PortfolioState(
        total_equity=100000.0,
        current_drawdown_pct=0.02,
        positions=[],
        sector_exposure_map={"TECHNOLOGY": 0.10}, # 10% Tech exposure
        gross_exposure_pct=0.4,
        net_exposure_pct=0.2
    )

@pytest.fixture
def default_decision():
    return StrategyDecision(
        symbol="AAPL",
        direction="LONG",
        selected_strategy="MOMENTUM",
        convergence_score=0.04,
        time_horizon="SWING",
        regime="TRENDING",
        sector="TECHNOLOGY"
    )

# A) Position Cap Adjustment
def test_position_cap_adjustment(engine, default_portfolio, default_config, default_decision):
    decision = default_decision # 4%, cap 5% -> OK
    result = engine.check_constraints(decision, default_portfolio, default_config)
    assert result.status == "APPROVE"
    assert result.approved_size_pct == 0.04

    # Proposed 8%, cap 5% -> ADJUST
    high_decision = StrategyDecision(
        symbol="TSLA", direction="LONG", selected_strategy="MOMENTUM", 
        convergence_score=0.08, time_horizon="SWING", regime="TRENDING", sector="TECHNOLOGY"
    )
    result = engine.check_constraints(high_decision, default_portfolio, default_config)
    assert result.status == "ADJUST"
    assert result.approved_size_pct == 0.05
    assert "Position cap applied" in result.adjustment_reason

# B) Sector Rejection
def test_sector_rejection(engine, default_portfolio, default_config):
    # Sector cap 25%. Current 24%. Proposed 3% -> 27% -> REJECT
    high_sector_portfolio = PortfolioState(
        total_equity=100000.0, current_drawdown_pct=0.02, positions=[],
        sector_exposure_map={"TECHNOLOGY": 0.24},
        gross_exposure_pct=0.4, net_exposure_pct=0.2
    )
    decision = StrategyDecision(
        symbol="NVDA", direction="LONG", selected_strategy="MOMENTUM",
        convergence_score=0.03, time_horizon="SWING", regime="TRENDING", sector="TECHNOLOGY"
    )
    result = engine.check_constraints(decision, high_sector_portfolio, default_config)
    assert result.status == "REJECT"
    assert "Sector exposure limit breached" in result.rejection_reason
    assert "SECTOR_LIMIT_REACHED" in result.risk_flags

# C) Gross Exposure Rejection
def test_gross_exposure_rejection(engine, default_portfolio, default_config, default_decision):
    high_gross_portfolio = PortfolioState(
        total_equity=100000.0, current_drawdown_pct=0.0, positions=[],
        sector_exposure_map={}, gross_exposure_pct=0.98, net_exposure_pct=0.2
    )
    result = engine.check_constraints(default_decision, high_gross_portfolio, default_config)
    assert result.status == "REJECT"
    assert "Gross exposure limit breached" in result.rejection_reason

# D) Net Exposure Boundary
def test_net_exposure_boundary(engine, default_portfolio, default_config, default_decision):
    boundary_portfolio = PortfolioState(
        total_equity=100000.0, current_drawdown_pct=0.0, positions=[],
        sector_exposure_map={}, gross_exposure_pct=0.5, net_exposure_pct=0.48
    )
    small_decision = StrategyDecision(
        symbol="AAPL", direction="LONG", selected_strategy="MOMENTUM",
        convergence_score=0.02, time_horizon="SWING", regime="TRENDING", sector="TECHNOLOGY"
    )
    result = engine.check_constraints(small_decision, boundary_portfolio, default_config)
    assert result.status == "APPROVE"

    large_decision = StrategyDecision(
        symbol="AAPL", direction="LONG", selected_strategy="MOMENTUM",
        convergence_score=0.03, time_horizon="SWING", regime="TRENDING", sector="TECHNOLOGY"
    )
    result = engine.check_constraints(large_decision, boundary_portfolio, default_config)
    assert result.status == "REJECT"
    assert "Net exposure limit breached" in result.rejection_reason

# E) Drawdown Kill Switch
def test_drawdown_kill_switch(engine, default_portfolio, default_config, default_decision):
    bad_portfolio = PortfolioState(
        total_equity=100000.0, current_drawdown_pct=0.12, positions=[],
        sector_exposure_map={}, gross_exposure_pct=0.4, net_exposure_pct=0.2
    )
    result = engine.check_constraints(default_decision, bad_portfolio, default_config)
    assert result.status == "REJECT"
    assert "Drawdown kill switch active" in result.rejection_reason
    assert result.approved_size_pct == 0.0

# F) Regime Scaling
def test_regime_scaling(engine, default_portfolio, default_config):
    stress_decision = StrategyDecision(
        symbol="AAPL", direction="LONG", selected_strategy="MOMENTUM",
        convergence_score=0.04, time_horizon="SWING", regime="STRESS", sector="TECHNOLOGY"
    )
    result = engine.check_constraints(stress_decision, default_portfolio, default_config)
    # 0.04 * 0.5 = 0.02
    assert result.status == "APPROVE"
    assert result.approved_size_pct == 0.02
    assert result.regime_scaling_applied == True

# G) Strategy-Specific Cap
def test_strategy_cap(engine, default_portfolio, default_config):
    scalp_decision = StrategyDecision(
        symbol="AAPL", direction="LONG", selected_strategy="SCALP",
        convergence_score=0.04, time_horizon="SCALP", regime="TRENDING", sector="TECHNOLOGY"
    )
    result = engine.check_constraints(scalp_decision, default_portfolio, default_config)
    assert result.status == "ADJUST"
    assert result.approved_size_pct == 0.02

# H) Deterministic Replay
def test_determinism(engine, default_portfolio, default_config, default_decision):
    results = [engine.check_constraints(default_decision, default_portfolio, default_config) for _ in range(10)]
    hashes = [r.input_hash for r in results]
    assert len(set(hashes)) == 1
    sizes = [r.approved_size_pct for r in results]
    assert max(sizes) - min(sizes) < 0.0000001
    assert results[0].risk_flags == results[1].risk_flags # Ensure list structure determinism

# Latency Guard
def test_latency_guard(engine, default_portfolio, default_config, default_decision):
    start = time.perf_counter()
    result = engine.check_constraints(default_decision, default_portfolio, default_config)
    assert result.latency_ms < 500
