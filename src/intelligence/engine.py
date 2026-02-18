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
import os as _os
import sys as _sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from intelligence.contracts import IntelligenceSnapshot, AttentionSignal, ResearchOverlay
from intelligence.symbol_universe import SymbolUniverseBuilder
from intelligence.generators.volatility import VolatilityAttention
from intelligence.generators.volume import VolumeAttention
from intelligence.generators.price import PriceBehavior

_INTEL_PROJECT_ROOT = _os.path.abspath(
    _os.path.join(_os.path.dirname(__file__), "..", "..", "..")
)
if _INTEL_PROJECT_ROOT not in _sys.path:
    _sys.path.insert(0, _INTEL_PROJECT_ROOT)

try:
    from automation.invariants.layer_integrations import gate_l7_convergence as _gate_l7
except ImportError:  # pragma: no cover
    import logging as _logging
    _logging.getLogger(__name__).critical(
        "CATASTROPHIC FIREWALL UNAVAILABLE — L7 invariant gate disabled"
    )
    raise

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
        
        # L6-L7 Opportunity Discovery Success Gate: Score Dispersion
        # High-Conviction Ideas must exhibit a minimum score variance of 0.15 across candidates.
        # Flat score distributions are invalid.
        if len(signals) > 1:
            scores = [s.metric_value for s in signals]
            
            # Calculate variance with latency logging (L7 Convergence Computation Observability)
            start_time = datetime.now()
            n = len(scores)
            mean = sum(scores) / n
            variance = sum((x - mean) ** 2 for x in scores) / n
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.info(f"Convergence Computation Latency: {latency_ms:.2f}ms | Variance: {variance:.4f}")
            
            MIN_SCORE_VARIANCE = 0.15
            if variance < MIN_SCORE_VARIANCE:
                self.logger.warning(
                    f"OPPORTUNITY DISCOVERY FAILURE: Score variance {variance:.4f} is below threshold {MIN_SCORE_VARIANCE}. "
                    "Invalidating all candidate signals for this cycle."
                )
                signals = []
        
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

        # ── L7 Catastrophic Invariant Gate ──────────────────────────────────
        # Signals without a conviction field default to "WATCHLIST" (exempt).
        # Any caller that sets conviction="HIGH" must supply ≥3 lenses.
        for _sig in enriched_signals:
            _sig_dict = _sig.to_dict() if hasattr(_sig, "to_dict") else vars(_sig)
            _gate_l7(_sig_dict)

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
