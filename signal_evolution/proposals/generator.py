from typing import List, Tuple
from signals.core.enums import Market, SignalCategory
from signal_meta_analytics.core.models import MetaInsight
from analytics.signal_reliability.models import ReliabilityReport
from signal_evolution.core.models import EvolutionProposal, AdvisoryScore
from signal_evolution.advisory.engine import AdvisoryEngine
from signal_evolution.core.enums import RecommendationType

class ProposalGenerator:
    def __init__(self, advisory_engine: AdvisoryEngine):
        self.engine = advisory_engine

    def generate_proposals(self, 
                          market: Market, 
                          categories: List[SignalCategory],
                          report: ReliabilityReport, 
                          insights: List[MetaInsight]) -> List[EvolutionProposal]:
        
        proposals = []
        
        # In reality, we'd split insights/report by category.
        # Here assuming singular input set covers the scope or we iterate.
        # Simplified: We treat the inputs as relevant to the requested categories.
        
        for cat in categories:
            # Filter insights for this category
            # (Mock filtering logic)
            cat_insights = [i for i in insights if i.signal_category == cat or i.signal_category == "ALL"]
            
            score = self.engine.calculate_score(report, cat_insights)
            rec_type, reason = self.engine.determine_recommendation(score)
            
            if rec_type != RecommendationType.NO_ACTION:
                # Evidence linking
                evidence = {
                    "insight_ids": [i.insight_id for i in cat_insights],
                    "health_score": score.category_health_score,
                    "calibration_error": score.calibration_error_magnitude
                }
                
                proposals.append(EvolutionProposal.create(
                    market=market,
                    category=cat,
                    rec=rec_type,
                    action=reason,
                    conf="HIGH",
                    score=score,
                    evidence=evidence
                ))
                
        return proposals
