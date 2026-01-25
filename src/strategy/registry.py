"""
Strategy Registry.
Defines declarative specifications for strategies.
NO LOGIC ALLOWED. Only Rules.
"""

STRATEGY_REGISTRY = {
    # -------------------------------------------------------------------------
    # MOMENTUM FAMILY
    # -------------------------------------------------------------------------
    
    # 1. BASELINE (Legacy V1 Reference)
    "STRATEGY_MOMENTUM_V1": {
        "category": "momentum",
        "intro_date": "2026-01-25",
        "factor_requirements": {
            "momentum": {
                "strength": "strong" # Using v1 Compat key
            }
        },
        "regime_requirements": {
            "allow": ["BULL_VOL", "BULL_CALM"]
        }
    },

    # 2. STRICT (New Baseline)
    # Requires Strong Level AND Accelerating
    "STRATEGY_MOMENTUM_STRICT_V1": {
        "category": "momentum",
        "intro_date": "2026-01-26",
        "factor_requirements": {
            "momentum": {
                "level": "strong",
                "acceleration": "accelerating"
            }
        },
        "regime_requirements": {
            "allow": ["BULL_VOL", "BULL_CALM"]
        }
    },

    # 3. ACCELERATING (Early Access)
    # Accepts Neutral/Strong Level IF Accelerating
    "STRATEGY_MOMENTUM_ACCELERATING_V1": {
        "category": "momentum",
        "intro_date": "2026-01-26",
        "factor_requirements": {
            "momentum": {
                "acceleration": "accelerating"
            }
        },
        "regime_requirements": {
            "allow": ["BULL_VOL", "BULL_CALM"]
        }
    },

    # 4. PERSISTENT (Stable Trend)
    # Accepts Persistent momentum regardless of acceleration
    "STRATEGY_MOMENTUM_PERSISTENT_V1": {
        "category": "momentum",
        "intro_date": "2026-01-26",
        "factor_requirements": {
            "momentum": {
                "persistence": "persistent"
            }
        },
        "regime_requirements": {
            "allow": ["BULL_VOL"]
        }
    },

    # -------------------------------------------------------------------------
    # VALUE / QUALITY FAMILY (Preserved)
    # -------------------------------------------------------------------------
    "STRATEGY_VALUE_QUALITY_V1": {
        "category": "value_quality",
        "intro_date": "2026-01-25",
        "factor_requirements": {}, # No specific factor gates defined yet (Assumed Robust)
        "regime_requirements": {
            "allow": ["BULL_VOL", "BULL_CALM", "BEAR_RISK_OFF"] # Robust across all
        }
    }
}
