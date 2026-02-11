import pytest
import json
import datetime
from pathlib import Path
from unittest.mock import patch

from src.evolution.strategy_eligibility_resolver import (
    _check_factor_contract,
    _check_regime_contract,
    resolve_strategy_eligibility,
    resolve_all_strategies,
    persist_daily_resolution,
)

# Test data
CURRENT_FACTORS = {
    "momentum": "CONFIRMED",
    "expansion": "EARLY",
    "dispersion": "NONE",
    "liquidity": "STRESSED",
    "volatility_factor": 1.5,
}

# --- Tests for _check_factor_contract ---

def test_check_factor_contract_empty():
    assert _check_factor_contract({}, CURRENT_FACTORS) == (True, None)

def test_check_factor_contract_min_state_pass():
    contract = {"momentum": {"min_state": "EMERGING"}}
    assert _check_factor_contract(contract, CURRENT_FACTORS) == (True, None)

def test_check_factor_contract_min_state_fail():
    factors = {"momentum": "NONE"}
    contract = {"momentum": {"min_state": "EMERGING"}}
    passed, reason = _check_factor_contract(contract, factors)
    assert not passed
    assert reason == "momentum: NONE < EMERGING"

def test_check_factor_contract_max_state_pass():
    contract = {"momentum": {"max_state": "CONFIRMED"}}
    assert _check_factor_contract(contract, CURRENT_FACTORS) == (True, None)

def test_check_factor_contract_max_state_fail():
    contract = {"liquidity": {"max_state": "COMPRESSED"}}
    passed, reason = _check_factor_contract(contract, CURRENT_FACTORS)
    assert not passed
    assert reason == "liquidity: STRESSED > COMPRESSED"

def test_check_factor_contract_exact_state_pass():
    contract = {"expansion": {"exact_state": "EARLY"}}
    assert _check_factor_contract(contract, CURRENT_FACTORS) == (True, None)

def test_check_factor_contract_exact_state_fail():
    contract = {"dispersion": {"exact_state": "BREAKOUT"}}
    passed, reason = _check_factor_contract(contract, CURRENT_FACTORS)
    assert not passed
    assert reason == "dispersion: NONE != BREAKOUT"
    
def test_check_factor_contract_min_variance_pass():
    contract = {"volatility_factor": {"min_variance": 1.2}}
    assert _check_factor_contract(contract, CURRENT_FACTORS) == (True, None)

def test_check_factor_contract_min_variance_fail():
    contract = {"volatility_factor": {"min_variance": 2.0}}
    passed, reason = _check_factor_contract(contract, CURRENT_FACTORS)
    assert not passed
    assert reason == "volatility_factor: 1.500 < required min 2.0"

def test_check_factor_contract_min_variance_non_numeric():
    contract = {"volatility_factor": {"min_variance": 1.0}}
    factors = {"volatility_factor": "HIGH"}
    passed, reason = _check_factor_contract(contract, factors)
    assert not passed
    assert reason == "Factor volatility_factor has non-numeric value 'HIGH'"
    
def test_check_factor_contract_min_variance_missing_factor():
    contract = {"volatility_factor": {"min_variance": 1.0}}
    factors = {"momentum": "CONFIRMED"}
    passed, reason = _check_factor_contract(contract, factors)
    assert not passed
    assert reason == "Factor value for volatility_factor not available"

def test_check_factor_contract_external_factors_fail():
    contract = {"yield_curve": {"min_state": "NORMAL"}}
    passed, reason = _check_factor_contract(contract, CURRENT_FACTORS)
    assert not passed
    assert reason == "yield_curve not yet measured"

def test_check_factor_contract_multiple_conditions_pass():
    contract = {
        "momentum": {"min_state": "CONFIRMED"},
        "liquidity": {"max_state": "STRESSED"},
        "volatility_factor": {"min_variance": 1.0}
    }
    assert _check_factor_contract(contract, CURRENT_FACTORS) == (True, None)

def test_check_factor_contract_multiple_conditions_fail():
    contract = {
        "momentum": {"min_state": "CONFIRMED"},
        "liquidity": {"exact_state": "NEUTRAL"},
    }
    passed, reason = _check_factor_contract(contract, CURRENT_FACTORS)
    assert not passed
    assert reason == "liquidity: STRESSED != NEUTRAL"


# --- Tests for _check_regime_contract ---

def test_check_regime_contract_empty():
    assert _check_regime_contract({}, "BULL_VOL") == (True, None)

def test_check_regime_contract_allowed_pass():
    contract = {"allow": ["BULL_VOL", "BULL_QUIET"]}
    assert _check_regime_contract(contract, "BULL_VOL") == (True, None)

def test_check_regime_contract_allowed_fail():
    contract = {"allow": ["BEAR_VOL", "BEAR_QUIET"]}
    passed, reason = _check_regime_contract(contract, "BULL_VOL")
    assert not passed
    assert reason == "Regime BULL_VOL not allowed"

def test_check_regime_contract_forbidden_pass():
    contract = {"forbid": ["NEUTRAL", "BEAR_VOL"]}
    assert _check_regime_contract(contract, "BULL_VOL") == (True, None)

def test_check_regime_contract_forbidden_fail():
    contract = {"forbid": ["BULL_VOL", "NEUTRAL"]}
    passed, reason = _check_regime_contract(contract, "BULL_VOL")
    assert not passed
    assert reason == "Regime BULL_VOL forbidden"

def test_check_regime_contract_allow_and_forbid():
    contract = {"allow": ["BULL_VOL"], "forbid": ["BEAR_VOL"]}
    assert _check_regime_contract(contract, "BULL_VOL") == (True, None)
    
    contract = {"allow": ["BULL_VOL"], "forbid": ["BULL_VOL"]}
    passed, reason = _check_regime_contract(contract, "BULL_VOL")
    assert not passed
    assert reason == "Regime BULL_VOL forbidden"

# --- Tests for resolve_strategy_eligibility ---

RESOLVED_AT = datetime.datetime.now().isoformat()

def test_resolve_strategy_eligibility_eligible():
    strategy_def = {
        "name": "Test Strat",
        "family": "Momentum",
        "regime_contract": {"allow": ["BULL_VOL"]},
        "factor_contract": {"momentum": {"min_state": "CONFIRMED"}},
        "activation_hint": "Good to go"
    }
    result = resolve_strategy_eligibility(
        "strat_001", strategy_def, "BULL_VOL", CURRENT_FACTORS, RESOLVED_AT
    )
    assert result["strategy_id"] == "strat_001"
    assert result["eligibility_status"] == "ELIGIBLE"
    assert result["primary_blocker"] is None
    assert result["blocking_reason"] is None
    assert result["activation_hint"] == "Good to go"

def test_resolve_strategy_eligibility_blocked_by_regime():
    strategy_def = {
        "name": "Test Strat",
        "regime_contract": {"forbid": ["NEUTRAL"]},
    }
    result = resolve_strategy_eligibility(
        "strat_002", strategy_def, "NEUTRAL", CURRENT_FACTORS, RESOLVED_AT
    )
    assert result["eligibility_status"] == "BLOCKED"
    assert result["primary_blocker"] == "REGIME"
    assert result["blocking_reason"] == "Regime NEUTRAL forbidden"

def test_resolve_strategy_eligibility_blocked_by_factor():
    strategy_def = {
        "name": "Test Strat",
        "factor_contract": {"momentum": {"exact_state": "EMERGING"}},
    }
    result = resolve_strategy_eligibility(
        "strat_003", strategy_def, "BULL_VOL", CURRENT_FACTORS, RESOLVED_AT
    )
    assert result["eligibility_status"] == "BLOCKED"
    assert result["primary_blocker"] == "FACTOR"
    assert result["blocking_reason"] == "momentum: CONFIRMED != EMERGING"

def test_resolve_strategy_eligibility_conditional_by_degrade():
    strategy_def = {
        "name": "Test Strat",
        "regime_contract": {"allow": ["BEAR_VOL"]},
        "safety_behavior": "degrade"
    }
    result = resolve_strategy_eligibility(
        "strat_004", strategy_def, "BULL_VOL", CURRENT_FACTORS, RESOLVED_AT
    )
    assert result["eligibility_status"] == "CONDITIONAL"
    assert result["primary_blocker"] == "REGIME"
    assert result["blocking_reason"] == "Regime BULL_VOL not allowed"

# --- Tests for resolve_all_strategies ---

MOCK_REGISTRY = {
    "strat_eligible": {
        "name": "Eligible Strat", "family": "Test",
        "regime_contract": {"allow": ["BULL_VOL"]},
        "factor_contract": {"momentum": {"min_state": "CONFIRMED"}},
    },
    "strat_blocked": {
        "name": "Blocked Strat", "family": "Test",
        "regime_contract": {"allow": ["BEAR_VOL"]},
    },
    "strat_conditional": {
        "name": "Conditional Strat", "family": "Test",
        "factor_contract": {"dispersion": {"exact_state": "BREAKOUT"}},
        "safety_behavior": "degrade",
    },
    "strat_no_contract": {
        "name": "No Contract Strat", "family": "Test",
    }
}

@patch('src.evolution.strategy_eligibility_resolver.STRATEGY_REGISTRY', MOCK_REGISTRY)
@patch('src.evolution.strategy_eligibility_resolver.get_evolution_version', return_value="1.2.3")
@patch('src.evolution.strategy_eligibility_resolver.get_frozen_date', return_value="2026-01-01")
def test_resolve_all_strategies(mock_version, mock_frozen_date):
    result = resolve_all_strategies("BULL_VOL", CURRENT_FACTORS)

    assert result["evolution_version"] == "1.2.3"
