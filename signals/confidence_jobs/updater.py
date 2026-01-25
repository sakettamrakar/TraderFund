import logging
import random
from datetime import datetime
from typing import List
from pathlib import Path
from signals.core.models import Signal
from signals.core.enums import Market, SignalState
from signals.repository.base import SignalRepository
from signals.confidence_engine.scorer import ConfidenceScorer
from signals.confidence_engine.decay import DecayCalculator
from signals.confidence_engine.inputs import ConfidenceContext

logger = logging.getLogger("ConfidenceJob")

class MockContextProvider:
    """
    Temporary provider until Indicator Engine is linked.
    Returns random but valid context data.
    """
    def get_context(self, signal: Signal) -> ConfidenceContext:
        return ConfidenceContext(
            volume_ratio=random.uniform(0.8, 2.5),
            volatility_z_score=random.uniform(-1.0, 3.0),
            indicator_agreement_count=random.randint(0, 3),
            market_trend_score=random.uniform(-1.0, 1.0)
        )

class ConfidenceUpdaterJob:
    def __init__(self, repo: SignalRepository):
        self.repo = repo
        self.scorer = ConfidenceScorer()
        self.decay = DecayCalculator()
        self.context_provider = MockContextProvider()

    def run(self, market: Market):
        logger.info(f"Starting Confidence Update Job for {market.value}")
        
        active_signals = self.repo.get_active_signals(market)
        logger.info(f"Found {len(active_signals)} active signals.")
        
        updated_count = 0
        now = datetime.utcnow()
        
        for sig in active_signals:
            try:
                # 1. Get Context
                context = self.context_provider.get_context(sig)
                
                # 2. Compute Fresh Score
                raw_conf, explanation = self.scorer.compute_score(sig, context)
                
                # 3. Apply Time Decay
                final_conf = self.decay.calculate_decayed_score(
                    initial_score=raw_conf,
                    trigger_time=sig.trigger_timestamp,
                    current_time=now,
                    horizon=sig.expected_horizon
                )
                
                # Add decay info to explanation
                explanation['raw_confidence'] = raw_conf
                explanation['decay_applied'] = raw_conf - final_conf
                explanation['calculated_at'] = now.isoformat()
                
                # 4. Check for Expiry logic (Optional here, or separate job)
                # If score drops too low, we might WEAKEN it.
                # Ideally, state transitions happen in a separate Lifestyle Manager.
                # Here we just update the score.
                
                # Optimization: Only save if changed significantly (> 1.0) or never scored
                old_conf = sig.confidence_score if sig.confidence_score is not None else -1.0
                
                if abs(final_conf - old_conf) > 0.1:
                    new_sig = sig.update_confidence(final_conf, explanation)
                    self.repo.save_signal(new_sig)
                    updated_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to update signal {sig.signal_id}: {e}")
                
        logger.info(f"Job Complete. Updated {updated_count} signals.")

if __name__ == "__main__":
    # Example standalone run
    from signals.repository.parquet_repo import ParquetSignalRepository
    repo = ParquetSignalRepository(Path("data/signals"))
    job = ConfidenceUpdaterJob(repo)
    job.run(Market.US)
