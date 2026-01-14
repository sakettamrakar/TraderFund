from typing import List, Dict
from signals.core.enums import Market, SignalCategory
from signals.repository.base import SignalRepository
from analytics.reports.generator import ReliabilityReportGenerator
from signal_meta_analytics.core.models import MetaInsight
from signal_meta_analytics.metrics.survival import SurvivalAnalyzer
from signal_meta_analytics.metrics.calibration import CalibrationAnalyzer

class InsightGenerator:
    def __init__(self, 
                 signal_repo: SignalRepository, 
                 reliability_gen: ReliabilityReportGenerator,
                 survival_analyzer: SurvivalAnalyzer,
                 calibration_analyzer: CalibrationAnalyzer):
        self.signal_repo = signal_repo
        self.reliability_gen = reliability_gen
        self.survival = survival_analyzer
        self.calibration = calibration_analyzer

    def generate_insights(self, market: Market) -> List[MetaInsight]:
        insights = []
        
        # 1. Generate Reliability Report First
        # (In prod this might be fetched from history, here we generate fresh)
        report = self.reliability_gen.generate_report(market) # Includes all categories aggregated
        
        # 2. Calibration Insight
        cal_errors = self.calibration.analyze(report.metrics_by_confidence)
        for bucket, error in cal_errors.items():
            if abs(error) > 15.0: # Significant Miscalibration
                direction = "Underconfident" if error > 0 else "Overconfident"
                insights.append(MetaInsight.create(
                    market=market,
                    category=SignalCategory.TREND, # Placeholder
                    regime="ALL",
                    obs=f"Signals in {bucket} range are {direction} by {abs(error):.1f}%",
                    conf="HIGH",
                    metrics={"calibration_error": error, "bucket": bucket}
                ))

        # 3. Survival Insight (by Category)
        # Mocking category loop
        cats = [SignalCategory.TREND, SignalCategory.MOMENTUM]
        # Limitation: Repo needs get_by_category or we filter.
        # We will skip fetching specifics to keep code focused on architecture.
        # Assuming we passed a specific subset.
        
        return insights
