"""Phase 5 Diagnostics: Manager Report Generator.

Produces a concise, decision-ready Markdown report from Phase-4 observation logs.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd

from .loader import SignalLogLoader
from .metrics import SignalMetrics
from .clustering import TimeOfDayClustering
from .simulations import WhatIfSimulator

logger = logging.getLogger(__name__)

class ManagerReportGenerator:
    """Generates a human-readable diagnostic report."""

    def __init__(self, log_dir: str = "observations/signal_reviews"):
        self.loader = SignalLogLoader(log_dir)
        self.df = None

    def load_data(self):
        """Load all observation logs."""
        self.df = self.loader.load_all_logs()

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """Generate the full manager report.

        Args:
            output_path: Optional path to save the report.

        Returns:
            Markdown report string.
        """
        if self.df is None or self.df.empty:
            self.load_data()

        if self.df.empty:
            return "# Diagnostic Report\n\nNo observation data available for analysis."

        metrics = SignalMetrics(self.df)
        clustering = TimeOfDayClustering(self.df)
        simulator = WhatIfSimulator(self.df)

        report_lines = []
        report_lines.append("# Phase 5 Diagnostic Report")
        report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Section 1: Executive Summary
        report_lines.append("## 1. Executive Summary")
        report_lines.append(f"- **Total Signals Observed**: {metrics.total_signals()}")
        ab = metrics.ab_ratio()
        report_lines.append(f"- **Overall A/B Ratio**: {ab:.1%}" if not pd.isna(ab) else "- **Overall A/B Ratio**: N/A")
        report_lines.append("")

        # Section 2: Signal Quality Breakdown
        report_lines.append("## 2. Signal Quality Breakdown")
        report_lines.append("### By Time of Day")
        bucket_summary = clustering.bucket_summary()
        for bucket, stats in bucket_summary.items():
            ab_str = f"{stats['ab_ratio']:.1%}" if stats['ab_ratio'] is not None else "N/A"
            report_lines.append(f"- **{bucket.replace('_', ' ').title()}**: {stats['signal_count']} signals, A/B: {ab_str}")
        report_lines.append("")

        report_lines.append("### By Symbol")
        freq_by_sym = metrics.frequency_by_symbol()
        for sym, count in freq_by_sym.head(5).items():
            report_lines.append(f"- {sym}: {count} signals")
        report_lines.append("")

        report_lines.append("### By Confidence Bucket")
        conf_by_class = metrics.confidence_by_class()
        for cls, conf in conf_by_class.items():
            report_lines.append(f"- Class {cls}: Avg Confidence {conf:.2f}")
        report_lines.append("")

        # Section 3: Failure Pattern Analysis
        report_lines.append("## 3. Failure Pattern Analysis")
        failure_clusters = clustering.failure_clusters()
        if failure_clusters:
            report_lines.append("C/D signals clustered in:")
            for bucket, count in failure_clusters.items():
                report_lines.append(f"- {bucket.replace('_', ' ').title()}: {count}")
        else:
            report_lines.append("No C/D signals found in the data.")
        report_lines.append("")

        # Section 4: What-If Insights
        report_lines.append("## 4. What-If Insights (Non-Binding)")
        simulations = simulator.run_all_simulations()
        for sim in simulations:
            old_ab = f"{sim['original_ab_ratio']:.1%}" if not pd.isna(sim['original_ab_ratio']) else "N/A"
            new_ab = f"{sim['new_ab_ratio']:.1%}" if not pd.isna(sim['new_ab_ratio']) else "N/A"
            report_lines.append(f"- **{sim['filter']}**: {sim['remaining_count']}/{sim['original_count']} signals remain ({sim['filtered_out_pct']}% filtered). A/B: {old_ab} → {new_ab}")
        report_lines.append("")

        # Section 5: Human Decision Checklist
        report_lines.append("## 5. Human Decision Checklist")
        report_lines.append("- [ ] Should any time window be avoided (e.g., first 15 minutes)?")
        report_lines.append("- [ ] Is the overall A/B ratio acceptable for live observation?")
        report_lines.append("- [ ] Are there symbols consistently underperforming?")
        report_lines.append("- [ ] Is refinement justified, or is more observation data needed?")
        report_lines.append("")

        report_lines.append("---")
        report_lines.append("*This report is for human judgment support only. No parameters have been changed.*")

        report_md = "\n".join(report_lines)

        if output_path:
            Path(output_path).write_text(report_md, encoding="utf-8")
            logger.info(f"Report saved to {output_path}")

        return report_md


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generator = ManagerReportGenerator()
    report = generator.generate_report()
    print(report)
