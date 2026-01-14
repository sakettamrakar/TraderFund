from typing import List, Dict, Tuple
from signal_meta_analytics.core.models import MetaInsight
from analytics.signal_reliability.models import ReliabilityReport
from signal_evolution.core.models import AdvisoryScore
from signal_evolution.core.enums import RecommendationType

class AdvisoryEngine:
    """
    Logic to convert Observations (Insights) into Advice (Recommendations).
    """
    
    def calculate_score(self, report: ReliabilityReport, insights: List[MetaInsight]) -> AdvisoryScore:
        # Mock Logic for scoring
        # In prod: weighted sum of survival, calibration, consistency
        
        # 1. Calibration Error Check
        cal_error = 0.0
        for i in insights:
            if "Overconfident" in i.observation:
                 load = i.metrics_payload.get('calibration_error', 0)
                 cal_error += abs(load)
        
        # 2. Health Score (Simple Inverse of error)
        health = max(0, 100 - (cal_error * 2))
        
        return AdvisoryScore(
            category_health_score=health,
            calibration_error_magnitude=cal_error,
            regime_sensitivity=0.5, # Placeholder
            stability_duration_days=30 # Placeholder
        )
        
    def determine_recommendation(self, score: AdvisoryScore) -> Tuple[RecommendationType, str]:
        if score.category_health_score < 40:
            return (RecommendationType.DEPRECATION_CANDIDATE, 
                    "Category health critically low. Consistent failure or massive overconfidence.")
            
        if score.calibration_error_magnitude > 20:
             return (RecommendationType.CONFIDENCE_RECALIBRATION_NEEDED,
                     f"Signal engine is miscalibrated by {score.calibration_error_magnitude:.1f}%.")
                     
        if score.category_health_score < 70:
             return (RecommendationType.MONITOR_CLOSELY,
                     "Performance is degrading. Watch closely.")
             
        return (RecommendationType.NO_ACTION, "Signal performing within bounds.")
