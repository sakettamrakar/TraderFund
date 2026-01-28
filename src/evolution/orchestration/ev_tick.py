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
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

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
        
        # 1. Ingest Real Data
        self._ingest_data()
        
        # 2. Update Contexts
        factor_path = self._build_factor_context()
        
        # 3. Run Watchers
        watcher_results = self._run_watchers(factor_path)

        # 3b. Build Macro Context (Explanatory / Read-Only)
        self._build_macro_context()
        
        # 4. Resolve Strategy Eligibility (NEW)
        resolution = self._resolve_strategy_eligibility(watcher_results)
        
        # 5. Governance & Logging
        self._log_execution(watcher_results, resolution)

        # 6. Capital Readiness Check (Read-Only)
        readiness = self._check_capital_readiness(resolution)
        
        # 7. Update Capital History (Narrative)
        self._record_capital_history_step(readiness, resolution)
        
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
        
    def _build_factor_context(self) -> Path:
        print("  [Step 2] Building Factor Context v1.3")
        # For EV-TICK, we might just look at the 'current' window or a specific tick window.
        # Here we mimic a single point update.
        # We can pass a dummy context_path if FactorContextBuilder requires file inputs,
        # or we might need to adapt FactorContextBuilder to work on 'latest'.
        # For now, we will create a dummy 'tick_context.json' to feed it, 
        # OR better, FactorContextBuilder takes a 'context_path' (regime context).
        # We should probably assume there's a 'latest' regime context.
        
        # Creating a temporary mock regime context for this tick
        tick_regime_path = self.output_dir / "regime_context.json"
        
        # Mocking regime data for the "Tick"
        # In production this comes from the live regime detector
        regime_data = {
            "regime_context": {
                "evaluation_window": {
                    "window_id": f"TICK-{self.timestamp}",
                    "start_date": self.timestamp,
                    "end_date": self.timestamp
                },
                "regime": "NEUTRAL",
                "confidence": 0.0, # Passive
                "details": "EV-TICK Generated"
            }
        }
        with open(tick_regime_path, "w") as f:
            json.dump(regime_data, f)
            
        output_path = self.output_dir / "factor_context.json"
        builder = FactorContextBuilder(context_path=tick_regime_path, output_path=output_path)
        builder.build()
        return output_path

    def _build_macro_context(self) -> Path:
        print("  [Step 3b] Building Macro Context (Read-Only)")
        macro_dir = PROJECT_ROOT / "docs" / "macro" / "context"
        builder = MacroContextBuilder(output_dir=macro_dir)
        
        # In a real scenario, this would come from `self._ingest_data` or a dedicated macro ingestor.
        # For this structural implementation, we use a mock current data updated with simple valid proxies.
        # This aligns with the "Explanation" layer design which consumes existing data.
        
        # We can try to read the latest ingested daily data files if they exist, 
        # or use hardcoded safe defaults for structural validation if live data isn't ready.
        # Given we just ran _ingest_data (Step 1), we could theoretically pass that data down.
        # For robustness in this step, we'll use a safe proxy dict.
        
        current_data = {
            "VIX": {"close": 20.0},
            "^TNX": {"close": 4.0},
            "HYG": {"close": 75.0},
            "LQD": {"close": 105.0} 
        }
        
        builder.build(current_data, self.timestamp)
        return macro_dir / "macro_context.json"

    def _run_watchers(self, factor_path: Path) -> Dict[str, Any]:
        print("  [Step 3] Running Diagnostic Watchers")
        results = {}
        window_id = f"TICK-{self.timestamp}"
        
        # Momentum
        mom_w = MomentumEmergenceWatcher()
        mom_w.watch(window_id, factor_path, self.output_dir)
        results['momentum'] = self._read_watcher_result(self.output_dir / "momentum_emergence.json")
        
        # Liquidity
        liq_w = LiquidityCompressionWatcher()
        liq_w.watch(window_id, factor_path, self.output_dir)
        results['liquidity'] = self._read_watcher_result(self.output_dir / "liquidity_compression.json")
        
        # Expansion
        exp_w = ExpansionTransitionWatcher()
        exp_w.watch(window_id, factor_path, self.output_dir)
        results['expansion'] = self._read_watcher_result(self.output_dir / "expansion_transition.json")
        
        # Dispersion
        dis_w = DispersionBreakoutWatcher()
        dis_w.watch(window_id, factor_path, self.output_dir)
        results['dispersion'] = self._read_watcher_result(self.output_dir / "dispersion_breakout.json")
        
        return results

    def _read_watcher_result(self, path: Path) -> Any:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return "N/A"

    def _resolve_strategy_eligibility(self, watcher_results: Dict[str, Any]) -> Dict[str, Any]:
        print("  [Step 4] Resolving Strategy Eligibility (Frozen Evolution v1)")
        
        # Extract current states from watcher results
        regime_path = self.output_dir / "regime_context.json"
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
        resolution = resolve_all_strategies(current_regime, current_factors)
        
        # Persist daily snapshot
        daily_dir = PROJECT_ROOT / "docs" / "evolution" / "daily_strategy_resolution"
        snapshot_path = persist_daily_resolution(resolution, daily_dir)
        print(f"    -> Snapshot: {snapshot_path.name}")
        print(f"    -> Eligible: {resolution['summary']['eligible']}/{resolution['summary']['total']}")
        
        # Also save to tick directory for correlation
        tick_resolution_path = self.output_dir / "strategy_resolution.json"
        with open(tick_resolution_path, 'w') as f:
            json.dump(resolution, f, indent=2)
        
        return resolution

    def _check_capital_readiness(self, resolution: Dict[str, Any]) -> Dict[str, Any]:
        print("  [Step 6] Verifying Capital Readiness (Read-Only)")
        
        # Get Regime
        regime_path = self.output_dir / "regime_context.json"
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
        readiness_path = self.output_dir / "capital_readiness.json"
        with open(readiness_path, 'w') as f:
            json.dump(readiness, f, indent=2)
            
        # Update Governance Log if NOT_READY
        return readiness

    def _record_capital_history_step(self, readiness: Dict[str, Any], resolution: Dict[str, Any]):
        print("  [Step 7] Recording Capital Narrative History")
        
        # Get Regime
        regime_path = self.output_dir / "regime_context.json"
        try:
            with open(regime_path, 'r') as f:
                regime_data = json.load(f)
            current_regime = regime_data.get("regime_context", {}).get("regime", "NEUTRAL")
        except:
            current_regime = "NEUTRAL"
            
        record = record_capital_history(self.output_dir, readiness, resolution, current_regime)
        print(f"    -> History Updated: {record['state']} ({record['reason']})")

    def _log_execution(self, watcher_results: Dict[str, Any], resolution: Dict[str, Any]):
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
### [{self.timestamp}] EV-TICK Passive Trace
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
