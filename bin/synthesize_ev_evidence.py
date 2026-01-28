import os
import csv
import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path("c:/GIT/TraderFund")
EVAL_DIR = PROJECT_ROOT / "docs/evolution/evaluation/ev"
CONTEXT_DIR = PROJECT_ROOT / "docs/evolution/context"
OUTPUT_FILE = PROJECT_ROOT / "docs/evolution/meta_analysis/evolution_metrics_table.csv"

def synthesize():
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        "activation_count": 0,
        "decision_count": 0,
        "failure_count": 0,
        "pnl_values": [],
        "rejection_reasons": defaultdict(int),
        "window_count": 0
    })))

    for root, dirs, files in os.walk(EVAL_DIR):
        if "strategy_activation_matrix.csv" in files:
            window_dir = Path(root)
            window_id = window_dir.name
            parts = window_dir.parts
            
            if 'historical' in parts and 'rolling' in parts and 'v1' in parts:
                profile_id = "EV-HISTORICAL-ROLLING-V1"
            elif 'forced' in parts and 'bull_calm' in parts and 'v1' in parts:
                profile_id = "EV-FORCED-BULL-CALM-V1"
            else:
                continue

            context_file = CONTEXT_DIR / profile_id / window_id / "regime_context.json"
            if not context_file.exists(): continue
            
            with open(context_file, 'r') as f:
                context_data = json.load(f)["regime_context"]
            
            regime = context_data["regime_code"]
            
            # 1. Activation Matrix
            matrix_file = window_dir / "strategy_activation_matrix.csv"
            with open(matrix_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    s_id = row["strategy_id"]
                    target = data[s_id][profile_id][regime]
                    target["activation_count"] += int(row["shadow"])
                    target["decision_count"] += int(row["decisions"])
                    target["failure_count"] += int(row["failures"])
                    target["window_count"] += 1

            # 2. Paper P&L
            pnl_file = window_dir / "paper_pnl_summary.csv"
            if pnl_file.exists():
                with open(pnl_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        s_id = row["strategy_id"]
                        target = data[s_id][profile_id][regime]
                        target["pnl_values"].append(float(row["total_pnl"]))

            # 3. Rejection Analysis
            reject_file = window_dir / "rejection_analysis.csv"
            if reject_file.exists():
                with open(reject_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        s_id = row["strategy_id"]
                        target = data[s_id][profile_id][regime]
                        reason = row["reason"]
                        count = int(row["count"])
                        target["rejection_reasons"][reason] += count

    # Determine Flags
    def get_flag(s_id, profile_dict):
        # profile_dict is data[s_id]
        # Robust: activates across multiple regimes, stable, low rejection variance
        # Fragile: frequent rejections for regime mismatch, unstable activation
        # Regime-Dependent: performs consistently only within specific regimes
        # Inconsistent: behaves differently across windows of same regime
        
        hist = profile_dict.get("EV-HISTORICAL-ROLLING-V1", {})
        forced = profile_dict.get("EV-FORCED-BULL-CALM-V1", {})
        
        # Simple heuristic for mock data analysis
        # If any rejections exist, let's flag based on dominant reason
        all_rejections = defaultdict(int)
        for p_id in profile_dict:
            for r_code in profile_dict[p_id]:
                for reason, count in profile_dict[p_id][r_code]["rejection_reasons"].items():
                    all_rejections[reason] += count
        
        if all_rejections.get("REGIME_MISMATCH", 0) > 10:
             return "🟡 REGIME-DEPENDENT"
        
        # If activation is 100% everywhere
        is_universal = True
        for p_id in profile_dict:
            for r_code in profile_dict[p_id]:
                met = profile_dict[p_id][r_code]
                if met["activation_count"] < met["decision_count"]:
                    is_universal = False
        
        if is_universal:
            return "🟢 ROBUST"
            
        return "⚠️ INCONSISTENT"

    # Final Summary Generation
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["strategy_id", "profile_id", "regime", "activation_rate", "rejection_rate", "dominant_rejection_reason", "shadow_fill_rate", "pnl_mean", "pnl_volatility", "evaluation_flag"])
        
        for s_id, profiles in data.items():
            # Flag is per strategy overall or per profile/strategy? Requirements say "For each strategy".
            flag = get_flag(s_id, profiles)
            
            for p_id, regimes in profiles.items():
                for r_code, metrics in regimes.items():
                    total_decisions = metrics["decision_count"]
                    activations = metrics["activation_count"]
                    rejections = sum(metrics["rejection_reasons"].values())
                    
                    activation_rate = activations / total_decisions if total_decisions > 0 else 0
                    rejection_rate = rejections / total_decisions if total_decisions > 0 else 0
                    shadow_fill_rate = activation_rate # Simplified for mock data
                    
                    dom_reason = "NONE"
                    if metrics["rejection_reasons"]:
                        dom_reason = max(metrics["rejection_reasons"], key=metrics["rejection_reasons"].get)
                    
                    pnls = metrics["pnl_values"]
                    pnl_mean = sum(pnls) / len(pnls) if pnls else 0
                    pnl_vol = 0
                    if len(pnls) > 1:
                        avg = pnl_mean
                        pnl_vol = (sum((x - avg)**2 for x in pnls) / len(pnls))**0.5
                    
                    writer.writerow([s_id, p_id, r_code, f"{activation_rate:.4f}", f"{rejection_rate:.4f}", dom_reason, f"{shadow_fill_rate:.4f}", f"{pnl_mean:.4f}", f"{pnl_vol:.4f}", flag])

if __name__ == "__main__":
    synthesize()
