from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from dashboard.backend.loaders.market_snapshot import load_market_snapshot
from dashboard.backend.loaders.strategies import load_strategy_eligibility

def load_system_narrative() -> Dict[str, Any]:
    """
    Generates a 3-5 sentence plain English summary of the system state.
    Reflects the current truth epoch ONLY.
    """
    snapshot = load_market_snapshot()
    eligibility = load_strategy_eligibility()
    
    regime = snapshot.get("regime", {}).get("state", "UNKNOWN")
    mom = snapshot.get("momentum", {}).get("state", "UNKNOWN")
    liq = snapshot.get("liquidity", {}).get("state", "UNKNOWN")
    exp = snapshot.get("expansion", {}).get("state", "NONE")
    
    eligible_count = sum(1 for s in eligibility.get("strategies", []) if s.get("eligible"))
    total_count = len(eligibility.get("strategies", []))
    
    # Narrative Templates (State-Closed / Backward-looking)
    sentences = []
    
    # Sentence 1: Regime
    if regime == "NEUTRAL":
        sentences.append("As of Truth Epoch TE-2026-01-30, the market environment is classified as neutral with no directional bias observed.")
    elif "BULL" in regime:
        sentences.append(f"In Truth Epoch TE-2026-01-30, the system observed {regime.replace('_', ' ').lower()} characteristics, maintaining a risk-on observation state.")
    elif "BEAR" in regime:
        sentences.append(f"The system recorded a {regime.replace('_', ' ').lower()} regime for Truth Epoch TE-2026-01-30, enforcing a capital preservation posture.")
    else:
        sentences.append(f"Market regime for Truth Epoch TE-2026-01-30 is {regime}, maintaining structural uncertainty.")

    # Sentence 2: Factors
    if mom == "NONE" and exp == "NONE":
        sentences.append("Low momentum and contracting volatility were measured, which accounts for the lack of structural conviction.")
    elif mom != "NONE" and exp != "NONE":
        sentences.append(f"Recorded data shows {mom.lower()} momentum paired with {exp.lower()} expansion for the current epoch.")
    else:
        sentences.append(f"Current recorded factors show {mom.lower()} momentum and {liq.lower()} liquidity.")

    # Sentence 3: Eligibility
    if eligible_count == 0:
        sentences.append("Governance-mandated safety gates have resulted in zero strategy eligibility to protect equity.")
    elif eligible_count < total_count / 3:
        sentences.append(f"Recorded state restricted eligibility to {eligible_count} out of {total_count} strategies, maintaining a defensive posture.")
    else:
        sentences.append(f"Structural alignment allowed for {eligible_count} strategies to meet eligibility criteria for observation.")

    # Sentence 4: Final Posture & Disclaimer
    sentences.append("The system is currently in 'Explanatory Observer' mode. This explanation reflects the current truth epoch (TE-2026-01-30) only and does not imply future action.")

    return {
        "summary": " ".join(sentences),
        "posture": "Defensive / Observational",
        "tone": "Mechanical"
    }

def load_system_blockers() -> List[Dict[str, Any]]:
    """
    Returns a checklist of high-level blocking conditions for the 'Why Nothing Is Happening' panel.
    State-closed and backward-looking only.
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
            "reason": f"Regime was recorded as {regime} for TE-2026-01-30."
        },
        {
            "id": "momentum_gate",
            "label": "Momentum Gate",
            "passed": mom != "NONE",
            "reason": f"No directional strength was detected in the current truth epoch." if mom == "NONE" else f"Momentum recorded as {mom}."
        },
        {
            "id": "volatility_gate",
            "label": "Volatility Gate",
            "passed": exp != "NONE",
            "reason": "Market was recorded in a contraction phase for TE-2026-01-30." if exp == "NONE" else f"Expansion recorded as {exp}."
        },
        {
            "id": "liquidity_gate",
            "label": "Liquidity Gate",
            "passed": liq != "STRESSED",
            "reason": f"Liquidity was recorded as {liq} for TE-2026-01-30."
        }
    ]
    
    return blockers
