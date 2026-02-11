"""
Strategy Registry.
Defines declarative specifications for strategies.
NO LOGIC ALLOWED. Only Rules.

Version: 2.0 (Full Universe)
Date: 2026-01-29
"""

STRATEGY_REGISTRY = {
    # =========================================================================
    # FAMILY A: TREND / MOMENTUM
    # =========================================================================
    
    "STRAT_MOM_TIMESERIES_V1": {
        "family": "momentum",
        "name": "Time-Series Momentum",
        "intent": "Follow absolute trend direction in individual assets",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_VOL", "BULL_CALM"],
            "forbid": ["BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "momentum": {"min_state": "EMERGING"},
            "expansion": {"min_state": "EARLY"}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Market must be expanding with confirmed momentum"
    },
    
    "STRAT_MOM_CROSSSECTION_V1": {
        "family": "momentum",
        "name": "Cross-Sectional Momentum",
        "intent": "Rank and select winners vs losers across universe",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_VOL", "BULL_CALM"],
            "forbid": ["BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "momentum": {"min_state": "EMERGING"},
            "dispersion": {"min_state": "BREAKOUT"},
            "score_dispersion": {"min_variance": 0.18}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Requires dispersion breakout to separate winners from losers"
    },
    
    "STRAT_MOM_BREAKOUT_V1": {
        "family": "momentum",
        "name": "Breakout / Trend-Following",
        "intent": "Enter on range expansion, ride established trends",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_VOL"],
            "forbid": ["BEAR_RISK_OFF", "BULL_CALM"]
        },
        "factor_contract": {
            "expansion": {"min_state": "CONFIRMED"}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Only in volatile uptrends with confirmed expansion"
    },
    
    # =========================================================================
    # FAMILY B: MEAN REVERSION
    # =========================================================================
    
    "STRAT_REVERT_SHORTTERM_V1": {
        "family": "mean_reversion",
        "name": "Short-Term Mean Reversion",
        "intent": "Fade 1-5 day overextensions",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM"],
            "forbid": ["BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "momentum": {"max_state": "NONE"},
            "liquidity": {"exact_state": "NEUTRAL"}
        },
        "safety_behavior": "degrade",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Activates in quiet markets when momentum is absent"
    },
    
    "STRAT_REVERT_STATISTICAL_V1": {
        "family": "mean_reversion",
        "name": "Statistical Reversion",
        "intent": "Trade Z-score extremes with defined lookback",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL"],
            "forbid": ["BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "dispersion": {"max_state": "NONE"}
        },
        "safety_behavior": "degrade",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Works when dispersion is low (assets move together)"
    },
    
    "STRAT_REVERT_VOLADJ_V1": {
        "family": "mean_reversion",
        "name": "Volatility-Adjusted Reversion",
        "intent": "Scale reversion bets by realized volatility",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "expansion": {"max_state": "NONE"}
        },
        "safety_behavior": "degrade",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Activates when volatility is contracting"
    },
    
    # =========================================================================
    # FAMILY C: VALUE
    # =========================================================================
    
    "STRAT_VALUE_DEEP_V1": {
        "family": "value",
        "name": "Deep Value",
        "intent": "Extreme P/E, P/B, or FCF discounts",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {},  # Regime-robust
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Regime-robust: Always eligible when evolution permits"
    },
    
    "STRAT_VALUE_RELATIVE_V1": {
        "family": "value",
        "name": "Relative Value",
        "intent": "Compare similar assets on valuation metrics",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {},  # Regime-robust
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Regime-robust: Always eligible when evolution permits"
    },
    
    "STRAT_VALUE_SPREAD_V1": {
        "family": "value",
        "name": "Valuation Spread Trades",
        "intent": "Long cheap vs short expensive within sector",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {},  # Regime-robust
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Regime-robust: Always eligible when evolution permits"
    },
    
    # =========================================================================
    # FAMILY D: QUALITY / DEFENSIVE
    # =========================================================================
    
    "STRAT_QUALITY_TILT_V1": {
        "family": "quality",
        "name": "Quality Tilt",
        "intent": "Overweight high ROE, low debt, stable margins",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {},  # Regime-robust
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Regime-robust: Always eligible when evolution permits"
    },
    
    "STRAT_QUALITY_LOWVOL_V1": {
        "family": "quality",
        "name": "Low Volatility",
        "intent": "Select low-beta, low-realized-vol stocks",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {},  # Regime-robust
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Regime-robust: Always eligible when evolution permits"
    },
    
    "STRAT_QUALITY_DEFENSIVE_V1": {
        "family": "quality",
        "name": "Defensive Carry",
        "intent": "Combine quality with dividend yield",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {},  # Regime-robust
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Regime-robust: Always eligible when evolution permits"
    },
    
    # =========================================================================
    # FAMILY E: CARRY / YIELD
    # =========================================================================
    
    "STRAT_CARRY_EQUITY_V1": {
        "family": "carry",
        "name": "Equity Carry",
        "intent": "Dividend yield + buyback yield",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM"],
            "forbid": ["BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "liquidity": {"exact_state": "NEUTRAL"}
        },
        "safety_behavior": "degrade",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Requires calm markets with normal liquidity"
    },
    
    "STRAT_CARRY_VOL_V1": {
        "family": "carry",
        "name": "Volatility Carry",
        "intent": "Short implied volatility vs realized",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM"],
            "forbid": ["BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "expansion": {"max_state": "NONE"}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Only in calm markets when expansion is absent"
    },
    
    "STRAT_CARRY_RATE_V1": {
        "family": "carry",
        "name": "Rate / Curve Carry",
        "intent": "Capture term premium along yield curve",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "yield_curve": {"slope": "positive"}  # External factor
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Requires positively sloped yield curve"
    },
    
    # =========================================================================
    # FAMILY F: VOLATILITY STRATEGIES
    # =========================================================================
    
    "STRAT_VOL_HARVEST_V1": {
        "family": "volatility",
        "name": "Volatility Harvesting",
        "intent": "Systematic short vol with defined hedges",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM"],
            "forbid": ["BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "expansion": {"max_state": "NONE"},
            "liquidity": {"exact_state": "NEUTRAL"}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Only in calm, liquid markets with no expansion"
    },
    
    "STRAT_VOL_VRP_V1": {
        "family": "volatility",
        "name": "Variance Risk Premium",
        "intent": "Capture IV > RV spread",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL"],
            "forbid": ["BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "vrp": {"state": "positive"}  # External factor
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Requires positive variance risk premium"
    },
    
    "STRAT_VOL_CONVEXITY_V1": {
        "family": "volatility",
        "name": "Convexity / Tail Hedges",
        "intent": "Long options for tail protection",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BEAR_RISK_OFF"],
            "forbid": ["BULL_CALM"]
        },
        "factor_contract": {
            "liquidity": {"min_state": "STRESSED"}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Activates only in stress regimes with liquidity crisis"
    },
    
    # =========================================================================
    # FAMILY G: RELATIVE / SPREAD STRATEGIES
    # =========================================================================
    
    "STRAT_SPREAD_PAIR_V1": {
        "family": "spread",
        "name": "Pair Trading",
        "intent": "Co-integrated pairs, mean-revert spread",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM"],
            "forbid": ["BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "dispersion": {"max_state": "NONE"}
        },
        "safety_behavior": "degrade",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Works when dispersion is low (pairs stay correlated)"
    },
    
    "STRAT_SPREAD_SECTOR_V1": {
        "family": "spread",
        "name": "Sector Spreads",
        "intent": "Long/short within sectors on relative value",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "dispersion": {"min_state": "BREAKOUT"},
            "score_dispersion": {"min_variance": 0.18}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Requires dispersion breakout to create spread opportunities"
    },
    
    "STRAT_SPREAD_FACTOR_V1": {
        "family": "spread",
        "name": "Factor Spreads",
        "intent": "Trade factor exposures (e.g., growth vs value)",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BULL_CALM", "BULL_VOL", "BEAR_RISK_OFF"]
        },
        "factor_contract": {
            "dispersion": {"min_state": "BREAKOUT"},
            "score_dispersion": {"min_variance": 0.18}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Requires dispersion breakout for factor differentiation"
    },
    
    # =========================================================================
    # FAMILY H: LIQUIDITY / STRESS STRATEGIES
    # =========================================================================
    
    "STRAT_STRESS_CRISIS_V1": {
        "family": "stress",
        "name": "Crisis Alpha",
        "intent": "Long convexity, short risk in stress",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BEAR_RISK_OFF"],
            "forbid": ["BULL_CALM", "BULL_VOL"]
        },
        "factor_contract": {
            "liquidity": {"min_state": "STRESSED"}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Only activates during crisis with stressed liquidity"
    },
    
    "STRAT_STRESS_LIQUIDITY_V1": {
        "family": "stress",
        "name": "Liquidity Provision",
        "intent": "Market-make in illiquid conditions",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BEAR_RISK_OFF"],
            "forbid": ["BULL_CALM"]
        },
        "factor_contract": {
            "liquidity": {"min_state": "COMPRESSED"}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Activates when liquidity is compressed or stressed"
    },
    
    "STRAT_STRESS_RISKOFF_V1": {
        "family": "stress",
        "name": "Risk-Off Protection",
        "intent": "Systematic de-risking triggers",
        "intro_date": "2026-01-29",
        "regime_contract": {
            "allow": ["BEAR_RISK_OFF"],
            "forbid": ["BULL_CALM", "BULL_VOL"]
        },
        "factor_contract": {
            "momentum": {"max_state": "NONE"}
        },
        "safety_behavior": "reject",
        "evolution_status": "EVOLUTION_ONLY",
        "activation_hint": "Activates in risk-off regime with no momentum"
    },
}

# --- Legacy Compatibility (Preserved) ---
# These are mapped to the new IDs for backward compatibility

LEGACY_STRATEGY_MAPPING = {
    "STRATEGY_MOMENTUM_V1": "STRAT_MOM_TIMESERIES_V1",
    "STRATEGY_MOMENTUM_STRICT_V1": "STRAT_MOM_TIMESERIES_V1",
    "STRATEGY_MOMENTUM_ACCELERATING_V1": "STRAT_MOM_CROSSSECTION_V1",
    "STRATEGY_MOMENTUM_PERSISTENT_V1": "STRAT_MOM_BREAKOUT_V1",
    "STRATEGY_VALUE_QUALITY_V1": "STRAT_VALUE_DEEP_V1",
}

def get_strategy(strategy_id: str) -> dict:
    """Get strategy by ID, handling legacy mappings."""
    if strategy_id in STRATEGY_REGISTRY:
        return STRATEGY_REGISTRY[strategy_id]
    if strategy_id in LEGACY_STRATEGY_MAPPING:
        return STRATEGY_REGISTRY[LEGACY_STRATEGY_MAPPING[strategy_id]]
    return None

def get_all_strategies() -> list:
    """Return all strategies as a list."""
    return [{"id": k, **v} for k, v in STRATEGY_REGISTRY.items()]

def get_strategies_by_family(family: str) -> list:
    """Return strategies filtered by family."""
    return [{"id": k, **v} for k, v in STRATEGY_REGISTRY.items() if v.get("family") == family]
