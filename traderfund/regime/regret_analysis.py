
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class RegretSummary:
    strategy: str
    regime_behavior: str
    signals_count: int
    blocked_count: int
    block_rate: float
    blocked_pnl: float  # What we would have made/lost if we took blocked trades
    prevented_loss: float # Negative part of blocked_pnl
    missed_profit: float # Positive part of blocked_pnl
    regret_score: float # prevented_loss - missed_profit (Higher is better)

class RegimeRegretAnalyzer:
    """
    Offline analyzer to quantify the value of Regime Engine gating.
    Matches Strategy Signals with Regime State and Outcome Data.
    """
    
    def __init__(self, tolerance_seconds: int = 5):
        self.tolerance = timedelta(seconds=tolerance_seconds)

    def load_data(self, 
                 regime_log_path: str, 
                 signal_log_path: str, 
                 outcome_log_path: Optional[str] = None) -> pd.DataFrame:
        """
        Loads and joins logs into a master DataFrame.
        Expected formats:
        - regime_log: JSONL from Shadow/Live Runner
        - signal_log: JSONL/CSV with {timestamp, symbol, strategy, signal_id}
        - outcome_log: CSV with {signal_id, pnl, mae, mfe, hit_stop} (Optional)
        """
        # 1. Load Regime Logs
        regime_records = []
        try:
            with open(regime_log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        d = json.loads(line)
                        meta = d.get('meta', {})
                        reg = d.get('regime', {})
                        shadow = d.get('shadow', {})
                        constraints = d.get('constraints', {})
                        
                        regime_records.append({
                            'timestamp': pd.to_datetime(meta.get('timestamp')),
                            'symbol': meta.get('symbol'),
                            'behavior': reg.get('behavior'),
                            'blocked_strategies': shadow.get('would_block', constraints.get('blocked_strategies', [])),
                            'throttled_strategies': shadow.get('would_throttle', constraints.get('throttled_strategies', []))
                        })
        except FileNotFoundError:
            print(f"File not found: {regime_log_path}")
            return pd.DataFrame()

        df_regime = pd.DataFrame(regime_records)
        df_regime.sort_values('timestamp', inplace=True)
        
        # 2. Load Signal Logs
        # Accepting a list of dicts for flexibility if paths not provided, 
        # but here we implement file loading.
        # Assuming simple CSV for signals for now or JSONL.
        # Let's support DataFrame input directly in 'analyze' for testing flexibility,
        # but this method assumes files.
        try:
            df_signals = pd.read_csv(signal_log_path) # Assumes CSV for signal log
            df_signals['timestamp'] = pd.to_datetime(df_signals['timestamp'])
        except Exception as e:
            print(f"Error loading signals: {e}")
            return pd.DataFrame()

        # 3. Load Outcomes (Optional)
        df_outcomes = pd.DataFrame()
        if outcome_log_path:
            try:
                df_outcomes = pd.read_csv(outcome_log_path)
            except Exception:
                pass

        # 4. As-Of Merge (Regime State at time of Signal)
        # We merge 'nearest' regime state prior to signal.
        
        df_signals.sort_values('timestamp', inplace=True)
        
        merged = pd.merge_asof(
            df_signals,
            df_regime,
            on='timestamp',
            by='symbol',
            direction='backward',
            tolerance=self.tolerance
        )
        
        # 5. Merge Outcomes
        if not df_outcomes.empty and 'signal_id' in merged.columns and 'signal_id' in df_outcomes.columns:
            merged = merged.merge(df_outcomes, on='signal_id', how='left')
        else:
            merged['pnl'] = 0.0 # Default if no outcome data
            
        return merged

    def compute_regret(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes regret metrics from the joined DataFrame.
        """
        if df.empty:
            return pd.DataFrame()

        results = []
        
        # Group by Strategy and Regime Behavior
        # We need to know if a signal was BLOCKED.
        # 'blocked_strategies' is a list.
        
        # Expand row for each strategy check? 
        # Assuming 'strategy' column in signals.
        
        if 'strategy' not in df.columns:
            return pd.DataFrame()

        for (strat, beh), group in df.groupby(['strategy', 'behavior']):
            total_signals = len(group)
            
            # Check if this strategy was in the blocked list for that row
            # Since 'blocked_strategies' is a list column, we apply check
            # We assume strategy name matches enum value (e.g. MOMENTUM)
            
            # Helper to check membership
            is_blocked = group['blocked_strategies'].apply(lambda x: strat in x if isinstance(x, list) else False)
            
            num_blocked = is_blocked.sum()
            
            # PnL of Blocked Trades
            # If we blocked it, we "prevented" that PnL.
            # If PnL was negative, we saved money (Prevented Loss).
            # If PnL was positive, we lost opportunity (Missed Profit).
            
            blocked_pnl_series = group.loc[is_blocked, 'pnl'].fillna(0.0)
            blocked_pnl_total = blocked_pnl_series.sum()
            
            prevented_loss = abs(blocked_pnl_series[blocked_pnl_series < 0].sum())
            missed_profit = blocked_pnl_series[blocked_pnl_series > 0].sum()
            
            # Regret Score = Prevented Loss - Missed Profit
            # Positive = Good (Regime saved us more than it cost us)
            regret_score = prevented_loss - missed_profit
            
            results.append({
                'strategy': strat,
                'regime_behavior': beh,
                'signals_count': total_signals,
                'blocked_count': num_blocked,
                'block_rate': round((num_blocked / total_signals) * 100, 2) if total_signals > 0 else 0.0,
                'blocked_pnl': blocked_pnl_total,
                'prevented_loss': prevented_loss,
                'missed_profit': missed_profit,
                'regret_score': regret_score
            })
            
        return pd.DataFrame(results)

    def generate_scorecard(self, regret_df: pd.DataFrame) -> str:
        """
        Generates a human-readable scorecard.
        """
        if regret_df.empty:
            return "No data for scorecard."

        lines = []
        lines.append("=== REGIME ENGINE REGRET ANALYSIS SCORECARD ===")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("")
        
        # Aggregated by Strategy
        for strat, group in regret_df.groupby('strategy'):
            lines.append(f"STRATEGY: {strat}")
            total_score = group['regret_score'].sum()
            lines.append(f"  NET REGRET SCORE: {total_score:+.2f} (Total Value Added)")
            lines.append("-" * 50)
            lines.append(f"  {'REGIME':<25} | {'BLOCK%':<8} | {'PREV. LOSS':<12} | {'MISS. PROFIT':<12} | {'NET':<10}")
            lines.append("-" * 50)
            
            for _, row in group.iterrows():
                lines.append(
                    f"  {row['regime_behavior']:<25} | "
                    f"{row['block_rate']:>6.1f}% | "
                    f"{row['prevented_loss']:>12.2f} | "
                    f"{row['missed_profit']:>12.2f} | "
                    f"{row['regret_score']:>+10.2f}"
                )
            lines.append("")
            
        return "\n".join(lines)
