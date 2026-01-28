from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from dashboard.backend.loaders.market_snapshot import load_market_snapshot
from dashboard.backend.loaders.strategies import load_strategy_eligibility

def load_system_narrative() -> Dict[str, Any]:
    """
    Generates a 3-5 sentence plain English summary of the system state.
    """
    snapshot = load_market_snapshot()
    eligibility = load_strategy_eligibility()
    
    regime = snapshot.get("regime", {}).get("state", "UNKNOWN")
    mom = snapshot.get("momentum", {}).get("state", "UNKNOWN")
    liq = snapshot.get("liquidity", {}).get("state", "UNKNOWN")
    exp = snapshot.get("expansion", {}).get("state", "NONE")
    
    eligible_count = sum(1 for s in eligibility.get("strategies", []) if s.get("eligible"))
    total_count = len(eligibility.get("strategies", []))
    
    # Narrative Templates
    sentences = []
    
    # Sentence 1: Regime
    if regime == "NEUTRAL":
        sentences.append("The market is currently in a stable, neutral state with no clear directional bias.")
    elif "BULL" in regime:
        sentences.append(f"The environment is currently exhibiting {regime.replace('_', ' ').title()} characteristics, favoring risk-on observation.")
    elif "BEAR" in regime:
        sentences.append(f"The system has detected a {regime.replace('_', ' ').title()} regime, prioritizing Capital Preservation and defensive monitoring.")
    else:
        sentences.append(f"The market regime is currently classified as {regime}, signaling a period of structural uncertainty.")

    # Sentence 2: Factors
    if mom == "NONE" and exp == "NONE":
        sentences.append("Internal dynamics show low momentum and contracting volatility, suggesting a lack of structural conviction.")
    elif mom != "NONE" and exp != "NONE":
        sentences.append(f"We are seeing {mom.lower()} momentum paired with {exp.lower()} expansion, which is a key precursor to trend formation.")
    else:
        sentences.append(f"Current factors show {mom.lower()} momentum and {liq.lower()} liquidity conditions.")

    # Sentence 3: Eligibility
    if eligible_count == 0:
        sentences.append("Because our safety gates are robust, all strategy families remain inactive to protect capital in the absence of edge.")
    elif eligible_count < total_count / 3:
        sentences.append(f"Only {eligible_count} out of {total_count} strategies are currently eligible, reflecting a highly selective and defensive posture.")
    else:
        sentences.append(f"Structural alignment allows for {eligible_count} strategies to be eligible for observation, indicating broad market participation.")

    # Sentence 4: Final Posture
    sentences.append("The system remains in 'Explanatory Observer' mode, intentionally inactive until higher-probability conditions emerge.")

    return {
        "summary": " ".join(sentences),
        "posture": "Defensive / Observational",
        "tone": "Calm"
    }

def load_system_blockers() -> List[Dict[str, Any]]:
    """
    Returns a checklist of high-level blocking conditions for the 'Why Nothing Is Happening' panel.
    """
    snapshot = load_market_snapshot()
    
    regime = snapshot.get("regime", {}).get("state", "UNKNOWN")
    mom = snapshot.get("momentum", {}).get("state", "UNKNOWN")
    exp = snapshot.get("expansion", {}).get("state", "NONE")
    liq = snapshot.get("liquidity", {}).get("state", "UNKNOWN")

    blockers = [
        {
            "id": "regime_gate",
            "label": "Regime Gate",
            "passed": regime not in ["UNKNOWN", "UNDEFINED", "BEAR_RISK_OFF"],
            "reason": "Regime must be stable or favorable for risk activities." if regime == "NEUTRAL" else f"Regime is {regime}."
        },
        {
            "id": "momentum_gate",
            "label": "Momentum Gate",
            "passed": mom != "NONE",
            "reason": "Wait for 'Emerging' or 'Confirmed' directional strength."
        },
        {
            "id": "volatility_gate",
            "label": "Volatility Gate",
            "passed": exp != "NONE",
            "reason": "Market is currently contracting; expansion is required for edge."
        },
        {
            "id": "liquidity_gate",
            "label": "Liquidity Gate",
            "passed": liq != "STRESSED",
            "reason": "Liquidity must be neutral or compressed, not stressed for safe entry."
        }
    ]
    
    return blockers
