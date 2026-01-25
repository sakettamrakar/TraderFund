"""Research Output - Generator (Builds reports from diffs/narratives)"""
import logging
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime, timedelta
from . import config
from .models import ResearchReport

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates research reports from narrative diffs."""
    
    def __init__(self):
        pass

    def _load_diff(self, symbol: str, date_str: str) -> Optional[dict]:
        path = config.DIFF_PATH / date_str / f"{symbol}_diff.parquet"
        if not path.exists():
            return None
        try:
            df = pd.read_parquet(path)
            # Convert numpy types to python types
            d = df.iloc[0].to_dict()
            for k, v in d.items():
                if hasattr(v, "tolist"):
                    d[k] = v.tolist()
            return d
        except Exception as e:
            logger.error(f"Error loading diff for {symbol}: {e}")
            return None

    def _load_narrative(self, symbol: str, date_str: str) -> Optional[dict]:
        path = config.NARRATIVE_PATH / date_str / f"{symbol}_narrative.parquet"
        if not path.exists():
            return None
        try:
            df = pd.read_parquet(path)
            d = df.iloc[0].to_dict()
            for k, v in d.items():
                if hasattr(v, "tolist"):
                    d[k] = v.tolist()
            return d
        except Exception as e:
            logger.error(f"Error loading narrative for {symbol}: {e}")
            return None

    def generate_daily_brief(self, date_str: str, symbols: List[str]) -> ResearchReport:
        """Generate daily research brief."""
        relevant_changes = []
        included = []
        risk_profile_counts = {"low": 0, "moderate": 0, "high": 0, "unknown": 0}
        
        narratives_cache = {}

        for sym in symbols:
            diff = self._load_diff(sym, date_str)
            narrative_data = self._load_narrative(sym, date_str)
            
            if narrative_data:
                narratives_cache[sym] = narrative_data
                rp = narrative_data.get("risk_context", "").split(" ")[0].lower() # Hacky parse
                if "low" in rp: risk_profile_counts["low"] += 1
                elif "moderate" in rp: risk_profile_counts["moderate"] += 1
                elif "high" in rp: risk_profile_counts["high"] += 1
                else: risk_profile_counts["unknown"] += 1

            if diff and diff["change_detected"]:
                included.append(sym)
                relevant_changes.append({
                    "symbol": sym,
                    "type": diff["change_type"],
                    "summary": diff["change_summary"],
                    "drivers": diff["change_drivers"]
                })
        
        # Build text summary
        summary_lines = [
            f"Analyzed {len(symbols)} symbols. Detected {len(relevant_changes)} meaningful changes."
        ]
        
        if not relevant_changes:
             summary_lines.append("Market structure remains stable compared to previous session.")
        else:
             promotions = [c['symbol'] for c in relevant_changes if c['type'] == 'promotion']
             degradations = [c['symbol'] for c in relevant_changes if c['type'] == 'degradation']
             if promotions:
                 summary_lines.append(f"Strengthening: {', '.join(promotions)}")
             if degradations:
                 summary_lines.append(f"Weakening: {', '.join(degradations)}")

        return ResearchReport.create(
            report_type="daily_brief",
            date_str=date_str,
            symbols=included,
            changes=relevant_changes,
            risk=risk_profile_counts,
            summary="\n".join(summary_lines),
            confidence="High - based on deterministic signal processing."
        )

    def format_text_report(self, report: ResearchReport) -> str:
        """Format report as human-readable text."""
        lines = []
        lines.append("═══════════════════════════════════════════")
        lines.append(f"DAILY RESEARCH BRIEF — {report.report_date}")
        lines.append(f"Market: {report.market_scope} | Changes: {len(report.key_changes)}")
        lines.append("═══════════════════════════════════════════")
        lines.append("")
        
        if report.key_changes:
            lines.append("KEY CHANGES")
            for change in report.key_changes:
                lines.append(f"• {change['symbol']}: {change['summary']}")
                if change['drivers']:
                    lines.append(f"  Drivers: {', '.join(change['drivers'])}")
            lines.append("")
        
        lines.append("RISK LANDSCAPE")
        lines.append(f"Low: {report.risk_summary.get('low',0)} | Moderate: {report.risk_summary.get('moderate',0)} | High: {report.risk_summary.get('high',0)}")
        lines.append("")
        
        lines.append("SUMMARY")
        lines.append(report.narrative_summary)
        lines.append("")
        lines.append("═══════════════════════════════════════════")
        return "\n".join(lines)
