import time
import hashlib
import json
from dataclasses import asdict
from typing import List, Optional
from src.models.constraint_models import (
    StrategyDecision,
    PortfolioState,
    RiskConfig,
    ConstraintDecision,
)

class ConstraintEngine:
    def __init__(self):
        self.strategy_caps = {
            "SCALP": 0.02,
            "POSITIONAL": 0.06,
            "VOLATILITY_EXPANSION": 0.03,
        }
        self.min_tradable_size = 0.005 # 0.5%

    def check_constraints(
        self,
        decision: StrategyDecision,
        portfolio: PortfolioState,
        config: RiskConfig
    ) -> ConstraintDecision:
        start_time = time.perf_counter()
        
        input_data = {
            "decision": asdict(decision),
            "portfolio": asdict(portfolio),
            "config": asdict(config)
        }
        input_json = json.dumps(input_data, sort_keys=True, default=str)
        input_hash = hashlib.sha256(input_json.encode()).hexdigest()

        if decision is None or portfolio is None or config is None:
             return self._create_rejection(
                symbol=decision.symbol if decision else "UNKNOWN",
                reason="INSUFFICIENT_CONTEXT",
                input_hash=input_hash,
                latency_ms=self._get_latency(start_time)
            )

        try:
            raw_size = decision.convergence_score
            adjustment_reason = ""
            risk_flags = []
            status = "APPROVE"
            regime_scaling_applied = False
            
            # --- 1. Regime Risk Scaling ---
            regime = decision.regime
            if regime == "STRESS":
                raw_size *= config.stress_scaling_factor
                adjustment_reason = "Regime scaling (STRESS)"
                risk_flags.append("REGIME_SCALING_APPLIED")
                regime_scaling_applied = True
            elif regime == "TRANSITION":
                raw_size *= config.transition_scaling_factor
                adjustment_reason = "Regime scaling (TRANSITION)"
                risk_flags.append("REGIME_SCALING_APPLIED")
                regime_scaling_applied = True
            
            # --- 2. Strategy-Specific Risk Law ---
            strategy_cap = self.strategy_caps.get(decision.selected_strategy, 1.0)
            if raw_size > strategy_cap:
                raw_size = strategy_cap
                adjustment_reason = f"Strategy cap applied ({decision.selected_strategy})"
                status = "ADJUST"

            # --- 3. Max Position Size Law (Catastrophic) ---
            if raw_size > config.max_position_pct:
                raw_size = config.max_position_pct
                adjustment_reason = "Position cap applied"
                status = "ADJUST"
                risk_flags.append("POSITION_CAP_APPLIED")

            # --- 4. Sector Exposure Law ---
            # "sector_exposure + approved_size <= max_sector_exposure"
            if decision.sector:
                current_sector_exposure = portfolio.sector_exposure_map.get(decision.sector, 0.0)
                if current_sector_exposure + raw_size > config.max_sector_exposure_pct:
                     return self._create_rejection(
                        decision.symbol, "Sector exposure limit breached", input_hash, self._get_latency(start_time),
                        risk_flags=["SECTOR_LIMIT_REACHED"]
                    )
            # If sector is None, we skip this check (or could reject if strictness required, but "Fail-Safe" for missing inputs is general context)
            # Given "Scope" didn't forbid optional sectors, we proceed.

            # --- 5. Gross Exposure Law ---
            if portfolio.gross_exposure_pct + raw_size > config.max_gross_exposure_pct:
                 return self._create_rejection(
                    decision.symbol, "Gross exposure limit breached", input_hash, self._get_latency(start_time)
                )

            # --- 6. Net Exposure Law ---
            current_net = portfolio.net_exposure_pct
            if decision.direction == "LONG":
                projected_net = current_net + raw_size
            else:
                projected_net = current_net - raw_size
            
            if abs(projected_net) > config.max_net_exposure_pct:
                 return self._create_rejection(
                    decision.symbol, "Net exposure limit breached", input_hash, self._get_latency(start_time)
                )

            # --- 7. Drawdown Kill Switch (Catastrophic) ---
            if portfolio.current_drawdown_pct >= config.max_drawdown_pct:
                 return self._create_rejection(
                    decision.symbol, "Drawdown kill switch active", input_hash, self._get_latency(start_time),
                    risk_flags=["DRAWDOWN_KILL_SWITCH"]
                )

            # --- 8. Minimum Tradable Size ---
            if raw_size < self.min_tradable_size:
                 return self._create_rejection(
                    decision.symbol, "Below minimum tradable size", input_hash, self._get_latency(start_time)
                )

            # --- Latency Guard ---
            latency = self._get_latency(start_time)
            if latency > 500:
                 return ConstraintDecision(
                    symbol=decision.symbol,
                    status="LATENCY_VIOLATION",
                    approved_size_pct=0.0,
                    adjustment_reason="Latency limit exceeded",
                    rejection_reason="Latency limit exceeded",
                    risk_flags=risk_flags,
                    regime_scaling_applied=regime_scaling_applied,
                    latency_ms=latency,
                    input_hash=input_hash
                )

            return ConstraintDecision(
                symbol=decision.symbol,
                status=status,
                approved_size_pct=raw_size,
                adjustment_reason=adjustment_reason,
                rejection_reason="",
                risk_flags=risk_flags,
                regime_scaling_applied=regime_scaling_applied,
                latency_ms=latency,
                input_hash=input_hash
            )

        except Exception as e:
             return self._create_rejection(
                decision.symbol if decision else "UNKNOWN",
                f"INTERNAL_ERROR: {str(e)}",
                input_hash,
                self._get_latency(start_time)
            )

    def _get_latency(self, start_time):
        return (time.perf_counter() - start_time) * 1000

    def _create_rejection(self, symbol, reason, input_hash, latency_ms, risk_flags=None):
        return ConstraintDecision(
            symbol=symbol,
            status="REJECT",
            approved_size_pct=0.0,
            adjustment_reason="",
            rejection_reason=reason,
            risk_flags=risk_flags if risk_flags else [],
            regime_scaling_applied=False,
            latency_ms=latency_ms,
            input_hash=input_hash
        )
