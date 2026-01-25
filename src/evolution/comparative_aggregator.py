"""
Comparative Meta-Analysis Aggregator.
Aggregates metrics from multiple evaluation profiles into a summary table.
"""
import argparse
import sys
import pandas as pd
from pathlib import Path
from typing import List

def aggregate_metrics(profile_roots: List[Path], output_path: Path):
    print(f"Aggregating metrics form {len(profile_roots)} profile roots...")
    
    aggregated_rows = []
    
    for root in profile_roots:
        if not root.exists():
            print(f"WARNING: Profile root {root} does not exist. Skipping.")
            continue
            
        # Recursive glob for all window directories (simple heuristic: look for rejections csv)
        # Structure: root/{profile_namespace}/.../{window_id}/rejection_analysis.csv
        rejection_files = list(root.rglob("rejection_analysis.csv"))
        
        for rej_file in rejection_files:
            window_dir = rej_file.parent
            # Assume sibling file for PnL
            pnl_file = window_dir / "paper_pnl_summary.csv"
            
            # Extract basic metadata
            try:
                # Load Rejection Data
                rej_df = pd.read_csv(rej_file)
                # Load PnL Data
                if pnl_file.exists():
                    pnl_df = pd.read_csv(pnl_file)
                else:
                    pnl_df = pd.DataFrame()
                
                # We need to pivot/summary per strategy
                strategies = set(rej_df["strategy_id"].unique()) if not rej_df.empty else set()
                if not pnl_df.empty:
                    strategies.update(pnl_df["strategy_id"].unique())
                
                for strat in strategies:
                    # Metrics from Rejection
                    rej_count = 0
                    rej_reason = "NONE"
                    if not rej_df.empty:
                        strat_rej = rej_df[rej_df["strategy_id"] == strat]
                        if not strat_rej.empty:
                            rej_count = strat_rej["count"].sum()
                            rej_reason = strat_rej["reason"].mode()[0] if not strat_rej["reason"].empty else "MIXED"
                    
                    # Metrics from PnL
                    regime = "UNKNOWN"
                    if not pnl_df.empty:
                        strat_pnl = pnl_df[pnl_df["strategy_id"] == strat]
                        if not strat_pnl.empty:
                            regime = strat_pnl["regime"].iloc[0]
                    
                    # Construct Row
                    row = {
                        "date": "2026-01-25", # Mock datestamp for aggregation
                        "window": window_dir.name,
                        "profile_source": root.name, # Heuristic
                        "regime": regime,
                        "strategy": strat,
                        "status": "ACTIVE" if rej_count == 0 else "LIMITED",
                        "condition": "ROBUST" if rej_count == 0 else "FRAGILE",
                        "pnl_paper": 0.0, # Placeholder
                        "rejections": rej_count,
                        "primary_reject_reason": rej_reason
                    }
                    aggregated_rows.append(row)
                    
            except Exception as e:
                print(f"Error processing {window_dir}: {e}")
                
    # Create final DataFrame
    df = pd.DataFrame(aggregated_rows)
    
    # Sort for readability
    if not df.empty:
        df = df.sort_values(by=["regime", "strategy"])
    
    df.to_csv(output_path, index=False)
    print(f"Successfully aggregated {len(df)} rows to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comparative Meta-Analysis Aggregator")
    parser.add_argument("--roots", nargs='+', type=Path, help="List of profile output roots to scan")
    parser.add_argument("--output", type=Path, default=Path("docs/evolution/meta_analysis/evolution_metrics_table.csv"), help="Output CSV path")
    args = parser.parse_args()
    
    try:
        aggregate_metrics(args.roots, args.output)
    except Exception as e:
        print(f"CRITICAL AGGREGATION FAILURE: {e}")
        sys.exit(1)
