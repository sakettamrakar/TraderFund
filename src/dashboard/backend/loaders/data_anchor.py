"""
Data Anchor Loader - Epistemic Restoration Layer.

Loads Truth Epoch and Data Provenance information for dashboard display.
This is a READ-ONLY endpoint that serves the epistemic state of the system.
"""
import json
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

def load_data_anchor(market: str = "US") -> Dict[str, Any]:
    """
    Load Data Anchor information for the specified market.
    Returns Truth Epoch + Market-specific Provenance + Confidence.
    """
    epistemic_dir = PROJECT_ROOT / "docs" / "epistemic"
    
    # Load Truth Epoch
    epoch_path = epistemic_dir / "truth_epoch.json"
    epoch_data = {}
    if epoch_path.exists():
        with open(epoch_path, 'r', encoding='utf-8') as f:
            epoch_data = json.load(f)
    
    # Load Market-specific Provenance
    provenance_path = epistemic_dir / f"data_provenance_{market}.json"
    provenance_data = {}
    if provenance_path.exists():
        with open(provenance_path, 'r', encoding='utf-8') as f:
            provenance_data = json.load(f)
    
    # Compute numeric sufficiency only
    sufficiency = provenance_data.get("sufficiency_analysis", {})
    missing_windows = provenance_data.get("missing_windows", [])
    
    return {
        "market": market,
        "truth_epoch": {
            "epoch_id": "TE-2026-01-30",
            "activation_time": epoch_data.get("epoch", {}).get("activation_time", "2026-01-30T00:00:00Z"),
            "mode": "REAL_ONLY",
            "immutable": True
        },
        "data_coverage": {
            "historical_years": next(
                (s.get("coverage_years", 0) for s in provenance_data.get("data_sources", [])), 
                0
            ),
            "required_lookback_days": 200,
            "available_records": next(
                (s.get("total_records", 0) for s in provenance_data.get("data_sources", [])), 
                0
            )
        },
        "date_range": next(
            (s.get("date_range", {}) for s in provenance_data.get("data_sources", [])),
            {"start": "UNKNOWN", "end": "UNKNOWN"}
        ),
        "sources": [
            {"symbol": s.get("symbol"), "source": s.get("source"), "format": s.get("format")}
            for s in provenance_data.get("data_sources", [])
        ],
        "missing_windows": missing_windows,
        "sufficiency": {
            k: {
                "available": v.get("available", 0),
                "required": v.get("required", 0),
                "status": v.get("status", "UNKNOWN")
            }
            for k, v in sufficiency.items()
        }
    }
