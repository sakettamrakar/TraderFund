import logging
from typing import List
from narratives.core.models import Narrative
from .models import Decision, DecisionAction

logger = logging.getLogger("DecisionEngine")

class DecisionEngine:
    ENTRY_THRESHOLD = 0.80
    EXIT_THRESHOLD = 0.50
    
    def __init__(self):
        pass
        
    def evaluate_narratives(self, narratives: List[Narrative]) -> List[Decision]:
        decisions = []
        
        for n in narratives:
            decision = self._evaluate_single(n)
            if decision.action != DecisionAction.DO_NOTHING:
                decisions.append(decision)
                
        return decisions
    
    def _evaluate_single(self, narrative: Narrative) -> Decision:
        # Simple Logic V1
        if narrative.confidence_score >= self.ENTRY_THRESHOLD:
            return Decision.create(
                narrative_id=narrative.narrative_id,
                action=DecisionAction.ENTER,
                confidence=narrative.confidence_score,
                rationale=f"Narrative confidence ({narrative.confidence_score:.2f}) exceeds entry threshold ({self.ENTRY_THRESHOLD}). Title: {narrative.title}",
                risk={"stop_loss": "ATE_SUPPORT", "allocation": "STANDARD"}
            )
            
        # TODO: Check if we are already in position for Exit Logic
        # For now, simplistic threshold check
        
        return Decision.create(
            narrative_id=narrative.narrative_id,
            action=DecisionAction.DO_NOTHING,
            confidence=narrative.confidence_score,
            rationale="Confidence insufficient for action."
        )
