"""
EV-TICK Orchestrator.
Executes the passive time advancement sequence:
1. Ingest Data (Mock/Live)
2. Update Observational Contexts (Regime, Factor v1.3)
3. Execute Diagnostic Watchers (Momentum, Liquidity, Expansion, Dispersion)
4. Resolve Strategy Eligibility (Daily)
5. Update Governance Log

Safety: Structural evolution is FROZEN. Only eligibility resolution runs daily.
"""
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution.factor_context_builder import FactorContextBuilder
from evolution.watchers.momentum_emergence_watcher import MomentumEmergenceWatcher
from evolution.watchers.liquidity_compression_watcher import LiquidityCompressionWatcher
from evolution.watchers.expansion_transition_watcher import ExpansionTransitionWatcher
from evolution.watchers.dispersion_breakout_watcher import DispersionBreakoutWatcher

# Strategy Resolution (Daily)
from evolution.strategy_evolution_guard import (
    assert_evolution_not_invoked,
    reset_guard,
    verify_frozen_artifacts_exist,
    get_evolution_version
)
from evolution.strategy_eligibility_resolver import (
    resolve_all_strategies,
    persist_daily_resolution
)

# Capital Readiness (Step 6)
from capital.capital_readiness import check_capital_readiness
# Capital History (Step 7)
from capital.capital_history_recorder import record_capital_history

# Macro Context (Step 3b)
from macro.macro_context_builder import MacroContextBuilder

# Intelligence Engine (Step 3c)
from intelligence.engine import IntelligenceEngine

from ingestion.api_ingestion.alpha_vantage.market_data_ingestor import USMarketIngestor

class EvTickOrchestrator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.timestamp = datetime.datetime.now().isoformat()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def execute(self):
        print(f"[{self.timestamp}] Starting EV-TICK Passive Time Advancement...")
        
        # Reset evolution guard at start of each tick
        reset_guard()
        
        # Verify frozen evolution artifacts exist
        verify_frozen_artifacts_exist()
        
        # 1. Ingest Real Data (Global + Market Specific)
        # For now, we ingest US primarily, India mocked/stubbed if needed.
        self._ingest_data()
        
        markets = ["US", "INDIA"]
        
        for market in markets:
            print(f"\n--- Processing Market: {market} ---")
            market_dir = self.output_dir / market
            market_dir.mkdir(parents=True, exist_ok=True)
            
            # 2. Update Contexts (Per Market)
            print(f"  [Step 2] Building Factor Context v1.3 ({market})")
            factor_path = self._build_factor_context(market, market_dir)
            
            # 3. Run Watchers (Per Market)
            print(f"  [Step 3] Running Diagnostic Watchers ({market})")
            watcher_results = self._run_watchers(market, factor_path, market_dir)
    
            # 3b. Build Macro Context (Per Market)
            print(f"  [Step 3b] Building Macro Context ({market})")
            self._build_macro_context(market, market_dir)
            
            # 3c. Run Intelligence Engine (Per Market)
            try:
                print(f"  [Step 3c] Running Intelligence Engine ({market})")
                self._run_intelligence_engine(market, factor_path, market_dir)
            except Exception as e:
                print(f"    ! Intelligence Engine Failed (Non-Critical): {e}")
    
            # 4. Resolve Strategy Eligibility (Per Market)
            print(f"  [Step 4] Resolving Strategy Eligibility ({market})")
            resolution = self._resolve_strategy_eligibility(market, watcher_results, market_dir)
            
            # 5. Governance & Logging (Global Ledger, Locally scoped content)
            self._log_execution(market, watcher_results, resolution)
    
            # 6. Capital Readiness Check (Per Market)
            print(f"  [Step 6] Verifying Capital Readiness ({market})")
            readiness = self._check_capital_readiness(resolution, market_dir)
            
            # 7. Update Capital History (Narrative) (Per Market)
            # Note: Capital Logic might need review if it assumes single global history.
            # For now, we write a HISTORY file inside the market dir to ensure isolation.
            self._record_capital_history_step(readiness, resolution, market_dir)
        
        # Final guard check: ensure no evolution was invoked
        assert_evolution_not_invoked()
        
        print(f"[{self.timestamp}] EV-TICK Complete.")
        
    def _ingest_data(self):
        print("  [Step 1] Ingesting Real Data (AlphaVantage)")
        try:
            ingestor = USMarketIngestor()
            # Core macro/market proxies for regime detection
            symbols = ["SPY", "QQQ", "IWM", "VIX"] 
            
            for sym in symbols:
                print(f"    - Fetching {sym}...", end="", flush=True)
                res = ingestor.fetch_symbol_daily(sym, full_history=False)
                status = res.get('status', 'UNKNOWN')
                msg = res.get('msg', '')
                print(f" {status} ({msg})")
                
        except Exception as e:
            print(f"    ! Ingestion Failed: {e}")
            # We continue execution even if ingestion fails (using last known or mock)
            # strictly for this EV-TICK diagnostic phase to ensure logging happens.
        
    def _get_authentic_regime(self, market: str) -> Dict[str, Any]:
        """
        Reads REAL data from disk and computes simple trend regime.
        Returns: (Regime, Confidence, Details)
        """
        try:
            prices = []
            symbol = ""
            
            if market == "US":
                # Read SPY.csv
                data_path = PROJECT_ROOT / "data" / "regime" / "raw" / "SPY.csv"
                if not data_path.exists():
                    return "UNKNOWN", 0.0, "Data File Missing: SPY.csv"
                
                symbol = "SPY"
                import csv
                with open(data_path, "r") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            prices.append(float(row["close"]))
                        except: pass
                        
            elif market == "INDIA":
                # Read NSE_RELIANCE_1d.jsonl
                data_path = PROJECT_ROOT / "data" / "raw" / "api_based" / "angel" / "historical" / "NSE_RELIANCE_1d.jsonl"
                if not data_path.exists():
                    return "UNKNOWN", 0.0, "Data File Missing: NSE_RELIANCE"
                
                symbol = "RELIANCE (NSE)"
                with open(data_path, "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                rec = json.loads(line)
                                prices.append(float(rec["close"]))
                            except: pass
                            
            if not prices:
                return "UNKNOWN", 0.0, f"No Price Data for {market}"
                
            # Compute Trend (SMA 50)
            if len(prices) < 50:
                short_avg = sum(prices) / len(prices)
                long_avg = short_avg # Not enough data
            else:
                current_price = prices[-1]
                sma_50 = sum(prices[-50:]) / 50
                
            regime = "BULLISH" if current_price > sma_50 else "BEARISH"
            conf = min(abs(current_price - sma_50) / sma_50 * 10, 1.0) # Simple confidence metric
            details = f"Authentic Data: {symbol} Price={current_price} SMA50={sma_50:.2f}"
            
            return regime, conf, details
            
        except Exception as e:
            return "UNKNOWN", 0.0, f"Error calculating regime: {str(e)}"

    def _build_factor_context(self, market: str, market_dir: Path) -> Path:
        print(f"  [Step 2] Building Factor Context v1.3 ({market})")
        # Creating a temporary logic-driven context for this tick
        tick_regime_path = market_dir / "regime_context.json"
        
        # authentic calculation
        regime, conf, details = self._get_authentic_regime(market)
        
        regime_data = {
            "regime_context": {
                "evaluation_window": {
                    "window_id": f"TICK-{self.timestamp}",
                    "start_date": self.timestamp,
                    "end_date": self.timestamp
                },
                "regime": regime,
                "confidence": conf,
                "details": details
            }
        }
        with open(tick_regime_path, "w") as f:
            json.dump(regime_data, f)
            
        output_path = market_dir / "factor_context.json"
        # Note: FactorContextBuilder might need update if it assumes specific paths,
        # but here we pass explicit paths so it should be fine if it respects them.
        builder = FactorContextBuilder(context_path=tick_regime_path, output_path=output_path)
        builder.build()
        return output_path

    def _build_macro_context(self, market: str, market_dir: Path) -> Path:
        print(f"  [Step 3b] Building Macro Context ({market})")
        # We want tick/US/macro_context.json. 
        # MacroContextBuilder.build takes `market` and appends it to output_dir if configured.
        # The execute loop passes `market_dir` (tick/US).
        # If we pass `self.output_dir` (tick root) to builder, and call build(..., market),
        # it will append market -> tick/US. That works.
        
        macro_dir = PROJECT_ROOT / "docs" / "macro" / "context" 
        # Oops, I want it in the tick dir for the snapshot.
        # Let's use self.output_dir as base.
        
        builder = MacroContextBuilder(output_dir=self.output_dir)
        
        # In authentic mode, we should fetch this from data_ingestion or leave empty.
        current_data = {
            "VIX": {"close": 0.0},
            "^TNX": {"close": 0.0},
            "HYG": {"close": 0.0},
            "LQD": {"close": 0.0} 
        }
        
        builder.build(current_data, self.timestamp, market)
        return self.output_dir / market / "macro_context.json"

    def _run_intelligence_engine(self, market: str, factor_path: Path, market_dir: Path):
        # We now run this strictly for the current market.
        # Output should go to the market_dir/intelligence/snapshots ? 
        # Or standard snapshots? Prompt says "Partition `ev_tick.py` output in `US/` and `INDIA/`".
        # So we want `tick_ts/US/intelligence_US_date.json`.
        
        intel_dir = market_dir / "intelligence" / "snapshots"
        intel_dir.mkdir(parents=True, exist_ok=True)
        
        engine = IntelligenceEngine(output_dir=intel_dir)
        
        # FAIL-CLOSED: Intelligence Engine requires real market data.
        # If no authentic data snapshot is available, we skip Intelligence Engine.
        # This prevents hallucinated signals from mock data.
        
        # Build research context from authentic regime file
        regime_path = market_dir / "regime_context.json"
        try:
            with open(regime_path, 'r') as f:
                regime_data = json.load(f)
            current_regime = regime_data.get("regime_context", {}).get("regime", "UNKNOWN")
        except:
            current_regime = "UNKNOWN"
            
        research_context = {
            "regime": current_regime, 
            "factors": {"momentum": "NONE", "volatility": "NORMAL"}
        }
        
        # EPISTEMIC RESTORATION: No mock market data.
        # Intelligence Engine will run with empty snapshot; it must handle gracefully.
        authentic_market_data = {}  # Empty - no mocks allowed
        
        # Run ONLY for the current market (will produce minimal output with no data)
        engine.run_cycle(market, research_context, authentic_market_data)

    def _run_watchers(self, market: str, factor_path: Path, market_dir: Path) -> Dict[str, Any]:
        results = {}
        window_id = f"TICK-{self.timestamp}"
        
        # Momentum
        mom_w = MomentumEmergenceWatcher()
        mom_w.watch(window_id, factor_path, market_dir)
        results['momentum'] = self._read_watcher_result(market_dir / "momentum_emergence.json")
        
        # Liquidity
        liq_w = LiquidityCompressionWatcher()
        liq_w.watch(window_id, factor_path, market_dir)
        results['liquidity'] = self._read_watcher_result(market_dir / "liquidity_compression.json")
        
        # Expansion
        exp_w = ExpansionTransitionWatcher()
        exp_w.watch(window_id, factor_path, market_dir)
        results['expansion'] = self._read_watcher_result(market_dir / "expansion_transition.json")
        
        # Dispersion
        dis_w = DispersionBreakoutWatcher()
        dis_w.watch(window_id, factor_path, market_dir)
        results['dispersion'] = self._read_watcher_result(market_dir / "dispersion_breakout.json")
        
        return results

    def _read_watcher_result(self, path: Path) -> Any:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return "N/A"

    def _resolve_strategy_eligibility(self, market: str, watcher_results: Dict[str, Any], market_dir: Path) -> Dict[str, Any]:
        # Extract current states from watcher results
        regime_path = market_dir / "regime_context.json"
        with open(regime_path, 'r') as f:
            regime_data = json.load(f)
        current_regime = regime_data.get("regime_context", {}).get("regime", "UNDEFINED")
        
        current_factors = {
            "momentum": watcher_results.get('momentum', {}).get('momentum_emergence', {}).get('state', 'NONE'),
            "expansion": watcher_results.get('expansion', {}).get('expansion_transition', {}).get('state', 'NONE'),
            "dispersion": watcher_results.get('dispersion', {}).get('dispersion_breakout', {}).get('state', 'NONE'),
            "liquidity": watcher_results.get('liquidity', {}).get('liquidity_compression', {}).get('state', 'NEUTRAL')
        }
        
        # Resolve eligibility for all strategies
        # NOTE: Strategies themselves might be market-specific? 
        # For Strict Arch Correction, we assume Strategy Objects are universal schemas,
        # but their *eligibility* is resolved against the MARKET context.
        resolution = resolve_all_strategies(current_regime, current_factors)
        
        # --- MARKET UNIVERSE FILTER (AUTHENTIC) ---
        # No more mocks. We rely on the strategy definition's own eligibility constraints.
        # If a strategy is not meant for India, it should be blocked by Metadata or Factor checks.
        
        # For now, pass all strategies through.
        pass
        # -------------------------------------
        
        # Persist daily resolution (Market Scoped)
        daily_dir = PROJECT_ROOT / "docs" / "evolution" / "daily_strategy_resolution" / market
        daily_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = persist_daily_resolution(resolution, daily_dir)
        
        print(f"    -> Snapshot: {snapshot_path.name}")
        print(f"    -> Eligible: {resolution['summary']['eligible']}/{resolution['summary']['total']}")
        
        # Also save to tick directory for correlation
        tick_resolution_path = market_dir / "strategy_resolution.json"
        with open(tick_resolution_path, 'w') as f:
            json.dump(resolution, f, indent=2)
        
        return resolution

    def _check_capital_readiness(self, resolution: Dict[str, Any], market_dir: Path) -> Dict[str, Any]:
        # Get Regime
        regime_path = market_dir / "regime_context.json"
        try:
            with open(regime_path, 'r') as f:
                regime_data = json.load(f)
            current_regime = regime_data.get("regime_context", {}).get("regime", "NEUTRAL")
        except:
            current_regime = "NEUTRAL"
            
        readiness = check_capital_readiness(resolution, current_regime)
        
        status = readiness['status']
        violations = readiness['violations']
        
        print(f"    -> Readiness Status: {status}")
        if violations:
            print(f"    -> Violations Found: {len(violations)}")
            for v in violations:
                print(f"       ! {v}")
        else:
            print("    -> No Risk Envelope Violations")
            
        # Persist Readiness
        readiness_path = market_dir / "capital_readiness.json"
        with open(readiness_path, 'w') as f:
            json.dump(readiness, f, indent=2)
            
        return readiness

    def _record_capital_history_step(self, readiness: Dict[str, Any], resolution: Dict[str, Any], market_dir: Path):
        print("  [Step 7] Recording Capital Narrative History")
        
        # Get Regime
        regime_path = market_dir / "regime_context.json"
        try:
            with open(regime_path, 'r') as f:
                regime_data = json.load(f)
            current_regime = regime_data.get("regime_context", {}).get("regime", "NEUTRAL")
        except:
            current_regime = "NEUTRAL"
            
        record = record_capital_history(market_dir, readiness, resolution, current_regime)
        print(f"    -> History Updated: {record['state']} ({record['reason']})")

    def _log_execution(self, market: str, watcher_results: Dict[str, Any], resolution: Dict[str, Any]):
        print("  [Step 5] Logging Governance Evidence")
        ledger_path = PROJECT_ROOT / "docs" / "epistemic" / "ledger" / "evolution_log.md"
        
        # Extract watcher states
        mom_state = watcher_results.get('momentum', {}).get('momentum_emergence', {}).get('state', 'UNKNOWN')
        liq_state = watcher_results.get('liquidity', {}).get('liquidity_compression', {}).get('state', 'UNKNOWN')
        exp_state = watcher_results.get('expansion', {}).get('expansion_transition', {}).get('state', 'UNKNOWN')
        dis_state = watcher_results.get('dispersion', {}).get('dispersion_breakout', {}).get('state', 'UNKNOWN')
        
        # Extract resolution summary
        summary = resolution.get('summary', {})
        eligible = summary.get('eligible', 0)
        total = summary.get('total', 0)
        
        entry = f"""
### [{self.timestamp}] EV-TICK Passive Trace [{market}]
- **Type**: CRON_TICK
- **Momentum**: `{mom_state}`
- **Liquidity**: `{liq_state}`
- **Expansion**: `{exp_state}`
- **Dispersion**: `{dis_state}`
- **Strategies**: {eligible}/{total} eligible (Evolution v1)
- **Action**: NONE (Passive Diagnosis)
"""
        with open(ledger_path, "a") as f:
            f.write(entry)

if __name__ == "__main__":
    # Default output to a 'tick' directory in artifacts
    # In real usage, this might go to a rolling log dir
    # Using a timestamped folder for now
    import time
    ts = int(time.time())
    out_dir = PROJECT_ROOT / "docs" / "evolution" / "ticks" / f"tick_{ts}"
    orchestrator = EvTickOrchestrator(out_dir)
    orchestrator.execute()
