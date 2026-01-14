import uuid
from datetime import datetime
from typing import Dict, List, Optional
from signals.core.enums import Market, SignalCategory
from signals.repository.base import SignalRepository
from analytics.signal_reliability.models import ReliabilityReport, ReliabilityMetric
from analytics.signal_reliability.evaluator import SignalEvaluator

class ReliabilityReportGenerator:
    def __init__(self, signal_repo: SignalRepository, evaluator: SignalEvaluator):
        self.signal_repo = signal_repo
        self.evaluator = evaluator

    def generate_report(self, market: Market, category: Optional[SignalCategory] = None) -> ReliabilityReport:
        # 1. Fetch Candidates
        # Currently repo only supports get_active_signals. 
        # Ideally we need get_historical_signals(date_range).
        # We will iterate what we have for now (assuming file repo scan).
        all_signals = self.signal_repo.get_active_signals(market) # This gets "Active" state, which might be wrong for history.
        
        # NOTE: In a real system we iterate HISTORY, not just ACTIVE.
        # But we previously implemented `get_signal_history` by ID. 
        # A full scan method `get_all_signals` is missing in the interface.
        # For evaluation proof-of-concept, we use the active ones assuming they are recent enough or we mock the list.
        # Let's assume we filter `all_signals` properly.
        
        if category:
            candidates = [s for s in all_signals if s.signal_category == category]
        else:
            candidates = all_signals
            
        # 2. Group by Confidence
        # Buckets: 0-20, 21-50, 51-75, 76-100
        buckets = {
            "NOISE": [],
            "WEAK": [],
            "MODERATE": [],
            "HIGH": []
        }
        
        for s in candidates:
            score = s.confidence_score if s.confidence_score else 0
            if score <= 20:
                buckets["NOISE"].append(s)
            elif score <= 50:
                buckets["WEAK"].append(s)
            elif score <= 75:
                buckets["MODERATE"].append(s)
            else:
                buckets["HIGH"].append(s)
                
        # 3. Evaluate Buckets
        metrics_map = {}
        for bucket_name, signals in buckets.items():
            metric = self.evaluator.evaluate_batch(signals, horizon_bars=5)
            metric.confidence_bucket = bucket_name
            metrics_map[bucket_name] = metric
            
        # 4. Overall
        overall_metric = self.evaluator.evaluate_batch(candidates, horizon_bars=5)
        overall_metric.confidence_bucket = "OVERALL"
        
        return ReliabilityReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.utcnow(),
            market=market,
            signal_category=category,
            period_start=datetime.min, # Placeholder
            period_end=datetime.utcnow(),
            metrics_by_confidence=metrics_map,
            overall_metric=overall_metric
        )
