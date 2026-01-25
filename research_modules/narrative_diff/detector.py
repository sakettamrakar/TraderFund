"""Narrative Diff - Detector (compares narratives and detects changes)"""
import logging
from typing import Optional, Dict, Any
from . import config
from .models import NarrativeDiff, ChangeType

logger = logging.getLogger(__name__)

class DiffDetector:
    """Detects meaningful changes between narratives."""
    
    def __init__(self):
        self.type_order = config.TYPE_ORDER
        self.state_order = config.STATE_ORDER
        self.risk_order = config.RISK_ORDER
        self.drift_threshold = config.SCORE_DRIFT_THRESHOLD
    
    def _get_order_index(self, value: str, order_list: list) -> int:
        try:
            return order_list.index(value)
        except ValueError:
            return -1
    
    def _compare_types(self, prev_type: str, curr_type: str) -> tuple:
        """Compare narrative types. Returns (changed, direction)."""
        if prev_type == curr_type:
            return (False, None)
        prev_idx = self._get_order_index(prev_type, self.type_order)
        curr_idx = self._get_order_index(curr_type, self.type_order)
        if curr_idx > prev_idx:
            return (True, "promotion")
        else:
            return (True, "degradation")
    
    def _compare_states(self, prev_state: str, curr_state: str) -> tuple:
        if prev_state == curr_state:
            return (False, None)
        prev_idx = self._get_order_index(prev_state, self.state_order)
        curr_idx = self._get_order_index(curr_state, self.state_order)
        if curr_idx > prev_idx:
            return (True, "strengthening")
        else:
            return (True, "weakening")
    
    def _compare_risk(self, prev_risk: str, curr_risk: str) -> tuple:
        if prev_risk == curr_risk:
            return (False, "unchanged")
        prev_idx = self._get_order_index(prev_risk, self.risk_order)
        curr_idx = self._get_order_index(curr_risk, self.risk_order)
        if curr_idx > prev_idx:
            return (True, "increased")
        else:
            return (True, "improved")
    
    def _get_score_changes(self, prev_evidence: dict, curr_evidence: dict) -> list:
        """Find stages with significant score changes."""
        drivers = []
        for key in ["structural_score", "energy_score", "participation_score", 
                    "momentum_score", "risk_score"]:
            prev = prev_evidence.get(key, 0) or 0
            curr = curr_evidence.get(key, 0) or 0
            delta = curr - prev
            if abs(delta) >= self.drift_threshold:
                stage = key.replace("_score", "").title()
                direction = "↑" if delta > 0 else "↓"
                drivers.append(f"{stage} {direction}{abs(delta):.0f}")
        return drivers
    
    def detect(self, current: Dict[str, Any], 
               previous: Optional[Dict[str, Any]] = None) -> NarrativeDiff:
        """Detect meaningful changes between narratives."""
        symbol = current["symbol"]
        curr_id = current["narrative_id"]
        
        # No previous narrative - first observation
        if previous is None:
            return NarrativeDiff.no_change(symbol, curr_id)
        
        prev_id = previous["narrative_id"]
        
        # Check type change
        type_changed, type_direction = self._compare_types(
            previous["narrative_type"], current["narrative_type"]
        )
        
        # Check state change  
        state_changed, state_direction = self._compare_states(
            previous["narrative_state"], current["narrative_state"]
        )
        
        # Check risk change
        prev_risk = previous.get("supporting_evidence", {}).get("risk_profile", "unknown")
        curr_risk = current.get("supporting_evidence", {}).get("risk_profile", "unknown")
        risk_changed, risk_impl = self._compare_risk(prev_risk, curr_risk)
        
        # Check confidence shift
        conf_shift = None
        if previous["confidence_level"] != current["confidence_level"]:
            conf_shift = f"{previous['confidence_level']} → {current['confidence_level']}"
        
        # Get driving changes
        drivers = self._get_score_changes(
            previous.get("supporting_evidence", {}),
            current.get("supporting_evidence", {})
        )
        
        # Determine if meaningful change occurred
        if not type_changed and not state_changed and not risk_changed and not conf_shift:
            return NarrativeDiff.no_change(symbol, curr_id, prev_id)
        
        # Classify change type
        if type_changed:
            if type_direction == "promotion":
                change_type = ChangeType.PROMOTION
                summary = f"{symbol} promoted: {previous['narrative_type']} → {current['narrative_type']}."
            else:
                change_type = ChangeType.DEGRADATION
                summary = f"{symbol} degraded: {previous['narrative_type']} → {current['narrative_type']}."
        elif state_changed:
            if state_direction == "strengthening":
                change_type = ChangeType.STABILIZATION
                summary = f"{symbol} strengthening: {previous['narrative_state']} → {current['narrative_state']}."
            else:
                change_type = ChangeType.DEGRADATION
                summary = f"{symbol} weakening: {previous['narrative_state']} → {current['narrative_state']}."
        elif risk_changed:
            change_type = ChangeType.RISK_CHANGE
            summary = f"{symbol} risk changed: {prev_risk} → {curr_risk}."
        else:
            change_type = ChangeType.STABILIZATION
            summary = f"{symbol} confidence shift: {conf_shift}."
        
        return NarrativeDiff.create(
            symbol=symbol,
            current_id=curr_id,
            previous_id=prev_id,
            change_type=change_type,
            summary=summary,
            drivers=drivers,
            risk_impl=risk_impl if risk_changed else "unchanged",
            confidence_shift=conf_shift,
        )
