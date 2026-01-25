from typing import List, Dict, Tuple
import numpy as np
from signals.core.models import Signal
from analytics.signal_reliability.models import ReliabilityMetric

class CalibrationAnalyzer:
    """
    Checks if Confidence (Predicted Probability) matches Reliability (Observed Probability).
    """
    def analyze(self, bucket_metrics: Dict[str, ReliabilityMetric]) -> Dict[str, float]:
        """
        Returns Calibration Error per bucket.
        positive = Underconfident (Metric > Score)
        negative = Overconfident (Metric < Score)
        """
        errors = {}
        
        # approximate bucket midpoints
        midpoints = {
            "NOISE": 10.0,    # 0-20
            "WEAK": 35.0,     # 21-50
            "MODERATE": 62.5, # 51-75
            "HIGH": 87.5      # 76-100
        }
        
        for bucket, metric in bucket_metrics.items():
            if metric.sample_size < 5:
                continue
                
            observed_acc = metric.directional_accuracy * 100.0
            predicted_conf = midpoints.get(bucket, 50.0)
            
            error = observed_acc - predicted_conf
            errors[bucket] = error
            
        return errors
