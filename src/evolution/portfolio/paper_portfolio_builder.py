"""
Paper Portfolio Builder (EV-PORTFOLIO-PAPER).
Counterfactual portfolio construction engine.
Measures strategy interaction, overlap, and redundancy without capital allocation.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class PaperPortfolioBuilder:
    """
    Builds a paper portfolio artifact based on strategy activation.
    """

    def build(self, window_id: str, activation_matrix_path: Path, output_dir: Path) -> None:
        if not activation_matrix_path.exists():
            print(f"[{window_id}] Portfolio Builder Skipped: No Activation Matrix.")
            return

        try:
            # 1. Load Activation Data
            strategies = []
            active_strategies = []
            
            with open(activation_matrix_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    strat_id = row['strategy_id']
                    # logic: decisions > 0 AND failures == 0 means "Active" in shadow mode
                    # But wait, activation matrix has 'decisions', 'shadow', 'failures'.
                    # A strategy is "Active" if it generated decisions.
                    decisions = int(row['decisions'])
                    
                    is_active = decisions > 0
                    
                    strategies.append({
                        "strategy_id": strat_id,
                        "activated": is_active,
                        "weight": 0.0 # Placeholder, calculated below
                    })
                    
                    if is_active:
                        active_strategies.append(strat_id)

            # 2. Calculate Weights (Equal Weight)
            count = len(strategies)
            if count > 0:
                weight = round(1.0 / count, 4)
                for s in strategies:
                    s["weight"] = weight

            # 3. Calculate Metrics
            active_count = len(active_strategies)
            overlap_score = 0.0
            
            # Simple Coincidence Metric:
            # If > 1 strategy active, we have "Overlap" in this window.
            # Real overlap requires trade-level comparison, but strategy-level activation coincidence 
            # is the proxy for "Regime Overlap".
            if active_count > 1:
                overlap_score = 1.0 # High overlap 
            elif active_count == 1:
                overlap_score = 0.0 # Unique
            else:
                overlap_score = 0.0 # None
            
            diversification = 1.0 - overlap_score if active_count > 0 else 0.0

            # Redundancy Clusters
            redundancy = []
            if active_count > 1:
                redundancy.append(active_strategies)

            # 4. Construct Output
            output_data = {
                "paper_portfolio": {
                    "version": "1.0.0",
                    "computed_at": datetime.now().isoformat(),
                    "window_id": window_id,
                    "strategies": strategies,
                    "metrics": {
                        "active_count": active_count,
                        "overlap_score": overlap_score,
                        "diversification_score": diversification,
                        "redundancy_clusters": redundancy
                    },
                    "constraints": {
                        "execution_disabled": True,
                        "capital_committed": 0.0
                    }
                }
            }

            output_path = output_dir / "paper_portfolio.json"
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
                
            print(f"  [Window: {window_id}] Portfolio Builder: {active_count} Active Strategies")

        except Exception as e:
            print(f"[{window_id}] Portfolio Builder Failed: {e}")
