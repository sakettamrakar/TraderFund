"""
Intelligence Engine (Read-Only).

Orchestrates the generation of market attention signals.
Strictly decoupled from execution.

Responsibilities:
1. Define Symbol Universe.
2. Run Safe Heuristics (Generators).
3. Apply Research Overlay (Context).
4. Persist Snapshot.
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from intelligence.contracts import IntelligenceSnapshot, AttentionSignal, ResearchOverlay
from intelligence.symbol_universe import SymbolUniverseBuilder
from intelligence.generators.volatility import VolatilityAttention
from intelligence.generators.volume import VolumeAttention
from intelligence.generators.price import PriceBehavior

class IntelligenceEngine:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.logger = logging.getLogger("IntelligenceEngine")
        self.universe_builder = SymbolUniverseBuilder(output_dir)
        
        # Instantiate Generators
        self.generators = [
            VolatilityAttention(),
            VolumeAttention(),
            PriceBehavior()
        ]
        
    def run_cycle(self, market: str, research_context: Dict[str, Any], market_data_snapshot: Dict[str, Any]) -> IntelligenceSnapshot:
        """
        Main execution cycle for a specific market.
        
        Args:
            market: "US" or "INDIA"
            research_context: Current Regime/Factor state
            market_data_snapshot: Dict of latest market data for symbols (Price, Vol, etc.)
        """
        self.logger.info(f"Running Intelligence Cycle for {market}")
        
        # 1. Build Universe
        universe = self.universe_builder.get_symbols(market)
        
        # 2. Run Generators
        signals = self._run_generators(universe, market, market_data_snapshot)
        
        # 3. Apply Research Overlay
        enriched_signals = self._apply_overlay(signals, research_context)
        
        # 4. Create Snapshot
        snapshot = IntelligenceSnapshot(
            timestamp=datetime.now().isoformat(),
            market=market,
            signals=enriched_signals,
            metadata={"source": "IntelligenceEngine v1.0", "universe_size": len(universe)}
        )
        
        # 5. Persist
        self._persist_snapshot(snapshot)
        
        return snapshot

    def _run_generators(self, universe: List[str], market: str, data: Dict[str, Any]) -> List[AttentionSignal]:
        signals = []
        for symbol in universe:
            # Get symbol data from snapshot (mocking structure if missing)
            sym_data = data.get(symbol, {})
            # If empty, skip (or use mock data for verification if needed)
            
            for gen in self.generators:
                sig = gen.evaluate(symbol, sym_data, market)
                if sig:
                    signals.append(sig)
        return signals

    def _apply_overlay(self, signals: List[AttentionSignal], context: Dict) -> List[AttentionSignal]:
        """
        Overlays research context onto raw signals.
        """
        regime = context.get("regime", "UNKNOWN")
        
        enriched = []
        for sig in signals:
            status = "ALLOWED"
            reason = f"Congruent with {regime} regime."
            
            # Simple heuristic overlay logic (Explanatory)
            if regime == "CRASH" or regime == "BEARISH_VOLATILE":
                status = "BLOCKED"
                reason = f"Blocked by {regime} Regime (Safety)."
            elif "VOLATILITY" in sig.signal_type and regime == "NEUTRAL":
                status = "CAUTION"
                reason = "Volatility expansion in NEUTRAL regime requires manual check."
            elif "LARGE_MOVE_DOWN" in sig.signal_type and regime == "BULLISH":
                status = "ATTENTION"
                reason = "Dip in Bullish Regime (Potential Value?)."
            
            overlay = ResearchOverlay(
                status=status,
                reason=reason,
                regime=regime
            )
            
            # Create new signal with overlay
            new_sig = AttentionSignal(
                symbol=sig.symbol,
                signal_type=sig.signal_type,
                domain=sig.domain,
                metric_label=sig.metric_label,
                metric_value=sig.metric_value,
                unit=sig.unit,
                baseline=sig.baseline,
                reason=sig.reason,
                explanation=sig.explanation,
                timestamp=sig.timestamp,
                market=sig.market,
                overlay=overlay
            )
            enriched.append(new_sig)
            
        return enriched

    def _persist_snapshot(self, snapshot: IntelligenceSnapshot):
        filename = f"intelligence_{snapshot.market}_{datetime.now().strftime('%Y-%m-%d')}.json"
        path = self.output_dir / filename
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(snapshot.to_dict(), f, indent=2)
            self.logger.info(f"Persisted snapshot to {path}")
