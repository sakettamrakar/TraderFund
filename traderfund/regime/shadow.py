
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from traderfund.regime.types import RegimeState, RegimeFactors, MarketBehavior
from traderfund.regime.calculator import RegimeCalculator
from traderfund.regime.core import StateManager
from traderfund.regime.gate import StrategyGate, StrategyClass
from traderfund.regime.observability import RegimeFormatter
from traderfund.regime.providers.trend import ADXTrendStrengthProvider
from traderfund.regime.providers.volatility import ATRVolatilityProvider
from traderfund.regime.providers.liquidity import RVOLLiquidityProvider
from traderfund.regime.providers.event import CalendarEventProvider

class ShadowRegimeRunner:
    """
    Runs the Regime Engine in Shadow Mode.
    Calculates regime and hypothetical gates but DOES NOT influence trading.
    Logs telemetry to a structured file.
    """
    def __init__(
        self, 
        log_file_path: str = "regime_shadow.jsonl",
        enabled: bool = True
    ):
        self.enabled = enabled
        self.log_file_path = log_file_path
        
        # Initialize Core Components
        self.calc = RegimeCalculator()
        self.manager = StateManager()
        self.gate = StrategyGate()
        
        # Initialize Providers (Default params, can be injected in real app)
        self.trend_provider = ADXTrendStrengthProvider()
        self.vol_provider = ATRVolatilityProvider()
        self.liq_provider = RVOLLiquidityProvider()
        self.event_provider = CalendarEventProvider()
        
        # Setup File Logger
        self._setup_logger()

    def _setup_logger(self):
        """
        Configures a separate logger for shadow telemetry to avoid polluting main logs.
        """
        self.logger = logging.getLogger("RegimeShadow")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False # Do not propagate to root
        
        # File Handler
        if self.enabled:
            handler = logging.FileHandler(self.log_file_path)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def on_tick(self, market_data: pd.DataFrame, symbol: str) -> Optional[RegimeState]:
        """
        Process a new market update in shadow mode.
        Returns the RegimeState for inspection (e.g. by unit tests),
        but primarily logs it to disk.
        """
        if not self.enabled:
            return None

        # 1. Compute Provider Outputs
        trend_strength = self.trend_provider.get_trend_strength(market_data)
        alignment = self.trend_provider.get_alignment(market_data)
        vol_ratio = self.vol_provider.get_volatility_ratio(market_data)
        liq_score = self.liq_provider.get_liquidity_score(market_data)
        event_data = self.event_provider.get_pressure(market_data)
        
        event_pressure = event_data['pressure']
        is_locked = event_data['is_lock_window']

        # 2. Calculate Raw Regime
        raw_regime = self.calc.calculate(
            trend_strength=trend_strength,
            trend_bias=alignment,
            volatility_ratio=vol_ratio,
            liquidity_score=liq_score,
            event_pressure=event_pressure,
            is_event_locked=is_locked
        )

        # 3. Update State Machine
        factors = RegimeFactors(
            trend_strength_norm=trend_strength,
            volatility_ratio=vol_ratio,
            liquidity_status="NORMAL" if liq_score > 0.5 else "DRY", # Mapper
            event_pressure_norm=event_pressure
        )
        
        state = self.manager.update(raw_regime, factors)

        # 4. Compute Hypothetical Gates
        blocked_strats = []
        throttled_strats = []
        
        for strat in StrategyClass:
            decision = self.gate.evaluate(state, strat)
            if not decision.is_allowed:
                blocked_strats.append(strat.value)
            elif decision.size_multiplier < 1.0:
                throttled_strats.append(strat.value)

        # 5. Log Telemetry
        telemetry_record = RegimeFormatter.to_dict(state, factors, symbol)
        # Enrich with shadow-specific fields
        telemetry_record['shadow'] = {
            "would_block": blocked_strats,
            "would_throttle": throttled_strats,
            "cooldown_active": self.manager.cooldown_timer > 0
        }
        
        self.logger.info(json.dumps(telemetry_record))
        
        return state

    def close(self):
        """Release file handlers"""
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
