
import json
import pandas as pd
from typing import Dict, Any, List

class RegimeAnalytics:
    """
    Offline analytics parser for Regime Engine JSONL logs.
    """
    @staticmethod
    def load_telemetry(log_file_path: str) -> List[Dict[str, Any]]:
        data = []
        try:
            with open(log_file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
        except FileNotFoundError:
            return []
        return data

    @staticmethod
    def compute_metrics(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Derives key performance metrics from telemetry logs.
        """
        if not data:
            return {}

        total_ticks = len(data)
        
        # 1. State Distribution
        behaviors = [d['regime']['behavior'] for d in data]
        behavior_counts = pd.Series(behaviors).value_counts()
        behavior_pct = (behavior_counts / total_ticks * 100).to_dict()
        
        # 2. Blocked Frequency
        # Strategies that would have been blocked
        blocked_strats = []
        for d in data:
            # Check shadow fields (from ShadowRunner) or constraint fields (from Formatter)
            # ShadowRunner puts enriched data in 'shadow'
            if 'shadow' in d:
                blocked_strats.extend(d['shadow']['would_block'])
            else:
                blocked_strats.extend(d['constraints']['blocked_strategies'])
                
        blocked_counts = pd.Series(blocked_strats).value_counts()
        blocked_pct = (blocked_counts / total_ticks * 100).to_dict()
        
        # 3. Stability (Transitions)
        transitions = 0
        prev_state = None
        for b in behaviors:
            if prev_state is not None and b != prev_state:
                transitions += 1
            prev_state = b
            
        return {
            "total_ticks": total_ticks,
            "regime_distribution_pct": behavior_pct,
            "strategy_block_rate_pct": blocked_pct,
            "total_transitions": transitions,
            "transition_rate": round(transitions / total_ticks, 4)
        }

    @staticmethod
    def print_report(log_file_path: str):
        data = RegimeAnalytics.load_telemetry(log_file_path)
        metrics = RegimeAnalytics.compute_metrics(data)
        
        print(f"--- Regime Engine Shadow Report ---")
        print(f"Log File: {log_file_path}")
        print(f"Total Ticks: {metrics.get('total_ticks', 0)}")
        print(f"Transitions: {metrics.get('total_transitions', 0)}")
        print("\nRegime Distribution (%):")
        for k, v in metrics.get('regime_distribution_pct', {}).items():
            print(f"  {k:<25}: {v:.1f}%")
        
        print("\nStrategy Block Rate (% of time blocked):")
        for k, v in metrics.get('strategy_block_rate_pct', {}).items():
            print(f"  {k:<25}: {v:.1f}%")
