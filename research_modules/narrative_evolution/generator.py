"""Narrative Evolution - Generator (creates narratives from stage outputs)"""
import logging
from typing import List, Optional
from . import config
from .models import Narrative, NarrativeType, StageEvidence

logger = logging.getLogger(__name__)

# Narrative summary templates
SUMMARY_TEMPLATES = {
    NarrativeType.STRUCTURAL_STRENGTH: "Structurally strong {symbol} with solid long-term alignment (score: {s1:.0f}). Energy and participation remain contained.",
    NarrativeType.ENERGY_BUILDUP: "{symbol} shows energy compression building (score: {s2:.0f}). Volatility contracting, range balance forming. Awaiting participation.",
    NarrativeType.EARLY_MOMENTUM: "Early participation emerging in {symbol} (score: {s3:.0f}). Volume and range expanding from compressed base. Momentum not yet confirmed.",
    NarrativeType.CONFIRMED_MOMENTUM: "{symbol} exhibits confirmed momentum (score: {s4:.0f}). Directional persistence and follow-through validated.",
    NarrativeType.MOMENTUM_FRAGILITY: "{symbol} has momentum (score: {s4:.0f}) but elevated fragility (risk: {s5:.0f}). Extension risk requires caution.",
    NarrativeType.DEGRADATION: "{symbol} showing degradation signals. High failure risk (score: {s5:.0f}). Momentum quality declining.",
    NarrativeType.NEUTRAL: "{symbol} in neutral state. No significant structural, energy, or momentum signals present.",
}

class NarrativeGenerator:
    """Generates narratives from stage outputs."""
    
    def __init__(self):
        self.thresholds = config.NARRATIVE_THRESHOLDS
    
    def classify_narrative_type(self, evidence: StageEvidence) -> NarrativeType:
        """Determine primary narrative type from evidence."""
        s1 = evidence.structural_score or 0
        s2 = evidence.energy_score or 0
        s3 = evidence.participation_score or 0
        s4 = evidence.momentum_score or 0
        s5 = evidence.risk_score or 0
        
        # Priority order: degradation > fragility > confirmed > early > energy > structural > neutral
        if s5 >= self.thresholds["degradation"].get("s5_risk", 60):
            return NarrativeType.DEGRADATION
        
        if s4 >= self.thresholds["momentum_fragility"].get("s4", 40) and \
           s5 >= self.thresholds["momentum_fragility"].get("s5_risk", 50):
            return NarrativeType.MOMENTUM_FRAGILITY
        
        if s4 >= self.thresholds["confirmed_momentum"].get("s4", 60):
            return NarrativeType.CONFIRMED_MOMENTUM
        
        if s3 >= self.thresholds["early_momentum"].get("s3", 50) and \
           s4 < self.thresholds["early_momentum"].get("s4_max", 50):
            return NarrativeType.EARLY_MOMENTUM
        
        if s2 >= self.thresholds["energy_buildup"].get("s2", 50) and \
           s3 < self.thresholds["energy_buildup"].get("s3_max", 40):
            return NarrativeType.ENERGY_BUILDUP
        
        if s1 >= self.thresholds["structural_strength"].get("s1", 60) and \
           s2 < self.thresholds["structural_strength"].get("s2_max", 40) and \
           s3 < self.thresholds["structural_strength"].get("s3_max", 40):
            return NarrativeType.STRUCTURAL_STRENGTH
        
        return NarrativeType.NEUTRAL
    
    def generate_summary(self, narrative_type: NarrativeType, 
                        symbol: str, evidence: StageEvidence) -> str:
        """Generate human-readable narrative summary."""
        template = SUMMARY_TEMPLATES.get(narrative_type, "{symbol} state undetermined.")
        return template.format(
            symbol=symbol,
            s1=evidence.structural_score or 0,
            s2=evidence.energy_score or 0,
            s3=evidence.participation_score or 0,
            s4=evidence.momentum_score or 0,
            s5=evidence.risk_score or 0,
        )
    
    def get_risk_context(self, evidence: StageEvidence) -> str:
        """Generate risk context string."""
        risk = evidence.risk_score or 0
        profile = evidence.risk_profile or "unknown"
        if risk >= 60:
            return f"High risk ({risk:.0f}). Posture: avoid."
        elif risk >= 30:
            return f"Moderate risk ({risk:.0f}). Posture: cautious."
        else:
            return f"Low risk ({risk:.0f}). Posture: monitor."
    
    def generate(self, symbol: str, evidence: StageEvidence,
                previous_narrative: Optional[Narrative] = None) -> Narrative:
        """Generate narrative from stage evidence."""
        narrative_type = self.classify_narrative_type(evidence)
        summary = self.generate_summary(narrative_type, symbol, evidence)
        risk_context = self.get_risk_context(evidence)
        
        # Determine what changed
        if previous_narrative:
            if previous_narrative.narrative_type != narrative_type.value:
                what_changed = f"Type changed: {previous_narrative.narrative_type} → {narrative_type.value}"
            else:
                what_changed = "Evidence updated, type unchanged"
        else:
            what_changed = "Initial generation"
        
        return Narrative.create(
            symbol=symbol,
            narrative_type=narrative_type,
            evidence=evidence,
            summary=summary,
            risk_context=risk_context,
            what_changed=what_changed,
        )
