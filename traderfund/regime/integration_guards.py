
import logging
import pandas as pd
import os
from pathlib import Path
from typing import Optional, NamedTuple
from datetime import datetime

from traderfund.regime.types import RegimeState, RegimeFactors, MarketBehavior
from traderfund.regime.calculator import RegimeCalculator, RawRegime
from traderfund.regime.core import StateManager
from traderfund.regime.gate import StrategyGate, StrategyClass, GateDecision
import json
from traderfund.regime.observability import RegimeFormatter
from traderfund.regime.providers.trend import ADXTrendStrengthProvider
from traderfund.regime.providers.volatility import ATRVolatilityProvider
from traderfund.regime.providers.liquidity import RVOLLiquidityProvider
from traderfund.regime.providers.event import CalendarEventProvider

logger = logging.getLogger(__name__)
telemetry_logger = logging.getLogger("RegimeTelemetry")
telemetry_logger.setLevel(logging.INFO)
# Prevent propagation to avoid polluting main logs if configured elsewhere
telemetry_logger.propagate = False 

# Ensure handler exists (simple check or re-add)
# In production, this should be cleaner, but for Phase 7 patch:
if not telemetry_logger.handlers:
    # Use append mode
    fh = logging.FileHandler("regime_shadow.jsonl", mode='a')
    fh.setFormatter(logging.Formatter('%(message)s'))
    telemetry_logger.addHandler(fh)

class GuardDecision(NamedTuple):
    allowed: bool
    size_multiplier: float
    reason: str
    regime_state: Optional[RegimeState]

class MomentumRegimeGuard:
    """
    Hard Gate integrating Regime Engine with Momentum Strategy.
    """
    def __init__(self, data_path: str = "data/processed/candles/intraday"):
        self.data_path = Path(data_path)
        
        # Initialize Core Components
        self.calc = RegimeCalculator()
        self.manager = StateManager()
        self.gate = StrategyGate()
        
        # Initialize Providers
        self.trend = ADXTrendStrengthProvider()
        self.vol = ATRVolatilityProvider()
        self.liq = RVOLLiquidityProvider()
        self.event = CalendarEventProvider()
        
        # State Cache (to avoid re-loading/re-calculating if called repeatedly per symbol)
        # Note: In a real live runner, we might clear this cache or manage state carefully.
        # For Phase 7 simple integration, we assume stateless checks or ephemeral state.
        self._state_cache = {} 

    def _load_data(self, symbol: str, exchange: str = "NSE") -> pd.DataFrame:
        """
        Loads same data as Momentum Strategy to ensure consistency.
        Phase 7 simplification: Reads from disk.
        """
        file_path = self.data_path / f"{exchange}_{symbol}_1m.parquet"
        if not file_path.exists():
            return pd.DataFrame()
        
        try:
            df = pd.read_parquet(file_path)
            # Ensure proper timestamp column
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            logger.error(f"Error loading data for regime check: {e}")
            return pd.DataFrame()

    def check_signal(self, signal_payload: dict) -> GuardDecision:
        """
        Evaluates a momentum signal against the current regime.
        
        Args:
            signal_payload: Dict containing 'symbol', 'timestamp', etc.
            
        Returns:
            GuardDecision (allowed, multiplier, reason, state)
        """
        # 0. Emergency Kill Switch / Mode Check
        mode = os.environ.get("REGIME_MODE", "SHADOW").upper() # Defaults to SHADOW if not set
        if mode == "OFF":
            return GuardDecision(True, 1.0, "REGIME_OFF: Legacy Mode", None)

        symbol = signal_payload.get('symbol')
        if not symbol:
            return GuardDecision(False, 0.0, "FAIL_SAFE: No symbol in signal", None)

        # 1. Load Data
        df = self._load_data(symbol)
        if df.empty or len(df) < 50:
            return GuardDecision(False, 0.0, "FAIL_SAFE: Insufficient history for regime", None)

        # 2. Compute Regime
        # (Stateless Providers)
        t_strength = self.trend.get_trend_strength(df)
        t_bias = self.trend.get_alignment(df)
        v_ratio = self.vol.get_volatility_ratio(df)
        l_score = self.liq.get_liquidity_score(df)
        e_data = self.event.get_pressure(df)
        
        raw = self.calc.calculate(
            trend_strength=t_strength,
            trend_bias=t_bias,
            volatility_ratio=v_ratio,
            liquidity_score=l_score,
            event_pressure=e_data['pressure'],
            is_event_locked=e_data['is_lock_window']
        )
        
        factors = RegimeFactors(
            trend_strength_norm=t_strength,
            volatility_ratio=v_ratio,
            liquidity_status="NORMAL" if l_score > 0.5 else "DRY",
            event_pressure_norm=e_data['pressure']
        )
        
        # Note: using a fresh StateManager implies NO HYSTERESIS MEMORY between calls 
        # if we instantiate new every time.
        # For Phase 7 "Hard Gate", if we run this in a loop, we should persist StateManager per symbol?
        # Yes, strictly speaking. But since the runner restarts or we might not have persistent state,
        # we will instantiate StateManager here. 
        # Caveat: This loses the "Persistence/Stability" benefit slightly (always starts at 0 persistence).
        # But it correctly enforces "EVENT_LOCK" and "UNDEFINED" which are immediate.
        # Ideally, we should check self._state_cache.
        
            
        if symbol in self._state_cache:
            manager = self._state_cache[symbol]
        else:
            manager = StateManager()
            self._state_cache[symbol] = manager
            
        # Warm-up / Replay to satisfy hysteresis
        # We process the last 15 bars (hysteresis max is usually ~5, cooldown ~30 but we can't replay that much easily stateless)
        # Using 15 bars covers most hysteresis toggles.
        lookback = 15
        subset = df.iloc[-lookback:] if len(df) > lookback else df

        final_state = None
        for i in range(len(subset)):
            # Create a growing window or just pass the full row?
            # Providers usually need history. But calculator needs scalar values.
            # We already calculated scalars on FULL df in Step 2.
            # But that was for the *latest* bar.
            # To warm up, we need scalars for *each* bar in subset.
            # Use rolling calculations? Too expensive to re-calc everything?
            # Optimization: Calculate indicators for the whole subset vectorized.
            
            # Re-calculating indicators for the window:
            # Slicing df up to i is correct but slow.
            # Better: Compute indicators on full DF once (vectorized), then iterate results.
            pass

        # Optimized Approach:
        # 1. Compute vectorized indicators for the last N rows
        # But our Providers define 'get_value(data) -> scalar'.
        # They read the *last* value.
        # So providing a window 'df.iloc[:end]' works.
        
        # To avoid calculating 15 times on full history, we assume providers are fast or we just take the hit for Phase 7 safety.
        # Given 1m candles, 15 iterations is acceptable.
        
        start_idx = len(df) - len(subset)
        for i in range(len(subset)):
            # Window ending at this bar
            window = df.iloc[:start_idx + i + 1]
            
            t_str = self.trend.get_trend_strength(window)
            t_aln = self.trend.get_alignment(window)
            v_rat = self.vol.get_volatility_ratio(window)
            l_scr = self.liq.get_liquidity_score(window)
            e_dat = self.event.get_pressure(window)
            
            raw_i = self.calc.calculate(t_str, t_aln, v_rat, l_scr, e_dat['pressure'], e_dat['is_lock_window'])
            fac_i = RegimeFactors(
                trend_strength_norm=t_str, 
                volatility_ratio=v_rat, 
                liquidity_status="NORMAL" if l_scr > 0.5 else "DRY", 
                event_pressure_norm=e_dat['pressure']
            )
            final_state = manager.update(raw_i, fac_i)

        state = final_state if final_state else manager.update(raw, factors) # Fallback if empty logic

        
        # 3. Gate Evaluation
        decision = self.gate.evaluate(state, StrategyClass.MOMENTUM)
        
        allowed = decision.is_allowed
        multiplier = decision.size_multiplier
        reason = decision.reason

        # SHADOW MODE OVERRIDE
        if mode == "SHADOW":
            if not allowed:
                 # Was BLOCKED
                 allowed = True
                 reason = f"[SHADOW-BLOCK] Would be BLOCKED: {decision.reason}"
                 multiplier = 1.0
            elif multiplier < 1.0:
                 # Was THROTTLED (but allowed was True)
                 reason = f"[SHADOW-THROTTLE] Would be x{multiplier}: {decision.reason}"
                 multiplier = 1.0
                 
                 
        # 4. Telemetry Logging
        try:
            telemetry_record = RegimeFormatter.to_dict(state, factors, symbol)
            telemetry_record['shadow'] = {
                "guard_decision": allowed,
                "multiplier": multiplier,
                "reason": reason,
                "mode": mode
            }
            telemetry_logger.info(json.dumps(telemetry_record))
        except Exception as e:
            # Telemetry failure should not crash trading
            logger.error(f"Telemetry logging failed: {e}")

        return GuardDecision(
            allowed=allowed,
            size_multiplier=multiplier,
            reason=reason,
            regime_state=state
        )
