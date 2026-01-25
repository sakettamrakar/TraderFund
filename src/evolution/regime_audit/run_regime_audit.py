#!/usr/bin/env python3
"""
Regime Audit Execution Runner (L12 - Evolution Phase / Regime Audit Execution).
Executes all regime audit modules and produces diagnostic artifacts.

SAFETY INVARIANTS:
- READ-ONLY execution.
- Does not modify data or logic.
- Produces explicit diagnostic artifacts.
- Idempotent and repeatable.

Usage:
    python run_regime_audit.py [--output-dir OUTDIR]
"""
import os
import sys
import json
import csv
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from evolution.regime_audit import (
    SymbolEnumeration,
    IngestionCoverageAudit,
    DepthAudit,
    AlignmentAudit,
    StateViabilityCheck,
    UndefinedAttributionReport
)


class RegimeAuditRunner:
    """
    Executes regime audit modules and produces diagnostic artifacts.
    
    SAFETY GUARANTEES:
    - All execution is read-only.
    - No data modification.
    - No logic modification.
    - Idempotent and repeatable.
    """
    
    def __init__(self, output_dir: str = "docs/diagnostics/regime"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.execution_timestamp = datetime.now()
        self.results: Dict[str, Any] = {}
        self.failures: List[str] = []
    
    def run_symbol_enumeration(self) -> Dict[str, Any]:
        """EV-RG-RUN-1: Execute symbol enumeration."""
        print("[EV-RG-RUN-1] Executing symbol enumeration...")
        
        enumerator = SymbolEnumeration()
        symbols = enumerator.enumerate_regime_requirements()
        report = enumerator.generate_requirements_report()
        
        # Validate
        if not symbols:
            self.failures.append("EV-RG-RUN-1: Required symbols list is empty")
            report["status"] = "FAILED"
        else:
            report["status"] = "SUCCESS"
        
        # Write CSV
        csv_path = self.output_dir / "symbol_coverage_matrix.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["symbol", "role", "lookback_days", "required_for", "description"])
            for sym in symbols:
                writer.writerow([
                    sym.symbol,
                    sym.role.value,
                    sym.lookback_days,
                    "|".join(sym.required_for),
                    sym.description
                ])
        
        self.results["symbol_enumeration"] = report
        print(f"  -> Output: {csv_path}")
        return report
    
    def run_ingestion_coverage(self) -> Dict[str, Any]:
        """EV-RG-RUN-2: Execute ingestion coverage audit."""
        print("[EV-RG-RUN-2] Executing ingestion coverage audit...")
        
        auditor = IngestionCoverageAudit()
        
        # Connect to real ingestion layer (data/regime/raw)
        data_dir = Path("data/regime/raw")
        symbol_data = {}
        
        # Load from CSVs if they exist
        for sym in ["QQQ", "SPY", "VIX", "^TNX", "^TYX", "HYG", "LQD"]:
            csv_path = data_dir / f"{sym}.csv"
            if csv_path.exists():
                dates = []
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            # Parse ISO format dates
                            dt = datetime.fromisoformat(row["date"]).date()
                            dates.append(dt)
                        except (ValueError, KeyError):
                            continue
                symbol_data[sym] = dates
            else:
                print(f"  [WARN] Missing data file for {sym}")
        
        # If no data found, fall back to empty dict (will cause audit failure, which is correct)

        
        lookback_requirements = {
            "QQQ": 252,
            "SPY": 252,
            "VIX": 63,
            "^TNX": 126,
            "^TYX": 126,
            "HYG": 63,
            "LQD": 63,
        }
        
        coverage = auditor.audit_all_symbols(symbol_data, lookback_requirements)
        report = auditor.generate_coverage_matrix()
        
        # Validate
        if not coverage:
            self.failures.append("EV-RG-RUN-2: Zero overlapping timestamps across symbols")
            report["status"] = "FAILED"
        else:
            report["status"] = "SUCCESS"
        
        # Write CSV
        csv_path = self.output_dir / "ingestion_coverage_report.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["symbol", "status", "earliest_date", "latest_date", "total_days", "missing_days", "coverage_pct"])
            for sym, details in report.get("coverage_details", {}).items():
                writer.writerow([
                    sym,
                    details["status"],
                    details["earliest_date"],
                    details["latest_date"],
                    details["total_days"],
                    details["missing_days"],
                    details["coverage_pct"]
                ])
        
        self.results["ingestion_coverage"] = report
        print(f"  -> Output: {csv_path}")
        return report
    
    def run_depth_audit(self) -> Dict[str, Any]:
        """EV-RG-RUN-3: Execute historical depth audit."""
        print("[EV-RG-RUN-3] Executing historical depth audit...")
        
        auditor = DepthAudit()
        
        # Use real data counts from previously loaded data if possible, or reload
        data_dir = Path("data/regime/raw")
        symbol_day_counts = {}
        
        for sym in ["QQQ", "SPY", "VIX", "^TNX", "^TYX", "HYG", "LQD"]:
            csv_path = data_dir / f"{sym}.csv"
            if csv_path.exists():
                with open(csv_path, 'r', encoding='utf-8') as f:
                    # Subtract 1 for header
                    count = sum(1 for line in f) - 1
                    symbol_day_counts[sym] = max(0, count)
            else:
                symbol_day_counts[sym] = 0
        
        lookback_requirements = {
            "QQQ": 252,
            "SPY": 252,
            "VIX": 63,
            "^TNX": 126,
            "^TYX": 126,
            "HYG": 63,
            "LQD": 63,
        }
        
        sufficiency = auditor.audit_all_depths(symbol_day_counts, lookback_requirements)
        report = auditor.generate_sufficiency_report()
        
        # Validate
        insufficient = auditor.get_insufficient_symbols()
        if insufficient:
            self.failures.append(f"EV-RG-RUN-3: Insufficient history for: {', '.join(insufficient)}")
            report["status"] = "FAILED"
        else:
            report["status"] = "SUCCESS"
        
        # Write markdown
        md_path = self.output_dir / "lookback_sufficiency_report.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Lookback Sufficiency Report\n\n")
            f.write(f"**Generated**: {self.execution_timestamp.isoformat()}\n\n")
            f.write(f"**Status**: {report['status']}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- Sufficient: {report['sufficient']}\n")
            f.write(f"- Marginal: {report['marginal']}\n")
            f.write(f"- Insufficient: {report['insufficient']}\n\n")
            f.write("## Details\n\n")
            f.write("| Symbol | Required | Available | Status | Gap |\n")
            f.write("|:-------|:---------|:----------|:-------|:----|\n")
            for sym, details in report.get("sufficiency_details", {}).items():
                f.write(f"| {sym} | {details['required_days']} | {details['available_days']} | {details['status']} | {details['gap_days']} |\n")
        
        self.results["depth_audit"] = report
        print(f"  -> Output: {md_path}")
        return report
    
    def run_alignment_audit(self) -> Dict[str, Any]:
        """EV-RG-RUN-4: Execute temporal alignment audit."""
        print("[EV-RG-RUN-4] Executing temporal alignment audit...")
        
        auditor = AlignmentAudit()
        
        # Use real data from CSVs
        data_dir = Path("data/regime/raw")
        symbol_dates = {}
        
        for sym in ["QQQ", "SPY", "VIX", "^TNX", "^TYX", "HYG", "LQD"]:
            csv_path = data_dir / f"{sym}.csv"
            if csv_path.exists():
                dates = set()
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            dt = datetime.fromisoformat(row["date"]).date()
                            dates.add(dt)
                        except (ValueError, KeyError):
                            continue
                symbol_dates[sym] = dates
            else:
                symbol_dates[sym] = set()
        
        alignments = auditor.audit_all_alignments(symbol_dates)
        report = auditor.generate_alignment_report()
        
        # Validate
        misaligned = [a for a in alignments if a.status.value == "MISALIGNED"]
        if len(misaligned) > len(alignments) / 2:
            self.failures.append("EV-RG-RUN-4: Alignment intersection below minimum viable range")
            report["status"] = "FAILED"
        else:
            report["status"] = "SUCCESS"
        
        # Write markdown
        md_path = self.output_dir / "temporal_alignment_report.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Temporal Alignment Report\n\n")
            f.write(f"**Generated**: {self.execution_timestamp.isoformat()}\n\n")
            f.write(f"**Status**: {report['status']}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- Total Pairs: {report['total_pairs_checked']}\n")
            f.write(f"- Aligned: {report['aligned_pairs']}\n")
            f.write(f"- Partial: {report['partial_pairs']}\n")
            f.write(f"- Misaligned: {report['misaligned_pairs']}\n\n")
            f.write("## Pairwise Alignment\n\n")
            f.write("| Symbol A | Symbol B | Status | Common | Alignment % |\n")
            f.write("|:---------|:---------|:-------|:-------|:------------|\n")
            for a in report.get("pairwise_alignment", []):
                f.write(f"| {a['symbol_a']} | {a['symbol_b']} | {a['status']} | {a['common_dates']} | {a['alignment_pct']}% |\n")
        
        self.results["alignment_audit"] = report
        print(f"  -> Output: {md_path}")
        return report
    
    def run_viability_check(self) -> Dict[str, Any]:
        """EV-RG-RUN-5: Execute state viability check."""
        print("[EV-RG-RUN-5] Executing state viability check...")
        
        checker = StateViabilityCheck()
        
        # Use results from previous audits
        coverage = self.results.get("ingestion_coverage", {})
        depth = self.results.get("depth_audit", {})
        alignment = self.results.get("alignment_audit", {})
        
        # Build inputs
        required_symbols = ["QQQ", "SPY", "VIX", "^TNX", "^TYX", "HYG", "LQD"]
        symbol_coverage = {s: d.get("status", "MISSING") for s, d in coverage.get("coverage_details", {}).items()}
        symbol_sufficiency = {s: d.get("status") == "SUFFICIENT" for s, d in depth.get("sufficiency_details", {}).items()}
        symbol_alignment = {s: True for s in required_symbols}  # Simplified
        
        check = checker.check_overall_viability(
            required_symbols=required_symbols,
            symbol_coverage=symbol_coverage,
            symbol_sufficiency=symbol_sufficiency,
            symbol_alignment=symbol_alignment
        )
        report = checker.generate_viability_report()
        
        # Validate
        if report["overall_status"] == "NOT_VIABLE":
            self.failures.append("EV-RG-RUN-5: Regime state cannot be constructed")
            report["status"] = "FAILED"
        else:
            report["status"] = "SUCCESS"
        
        # Write markdown
        md_path = self.output_dir / "state_viability_report.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# State Construction Viability Report\n\n")
            f.write(f"**Generated**: {self.execution_timestamp.isoformat()}\n\n")
            f.write(f"**Status**: {report['status']}\n\n")
            f.write(f"**Overall Viability**: {report['overall_status']}\n\n")
            f.write("## Blocking Reasons\n\n")
            for reason in report.get("blocking_reasons", []):
                f.write(f"- {reason}\n")
            f.write("\n## Missing Inputs\n\n")
            for inp in report.get("missing_inputs", []):
                f.write(f"- {inp}\n")
            f.write(f"\n## Recommendation\n\n{report.get('recommendation', 'None')}\n")
        
        self.results["viability_check"] = report
        print(f"  -> Output: {md_path}")
        return report
    
    def run_undefined_attribution(self) -> Dict[str, Any]:
        """EV-RG-RUN-6: Execute undefined regime attribution."""
        print("[EV-RG-RUN-6] Executing undefined regime attribution...")
        
        reporter = UndefinedAttributionReport()
        
        # Simulate undefined regime occurrences based on previous audit results
        depth = self.results.get("depth_audit", {})
        coverage = self.results.get("ingestion_coverage", {})
        
        missing_symbols = coverage.get("missing_symbols", [])
        insufficient_symbols = depth.get("insufficient_symbols", [])
        
        # Create attribution for simulated undefined regimes
        if missing_symbols or insufficient_symbols:
            reporter.attribute_undefined(
                timestamp=datetime.now(),
                missing_symbols=missing_symbols,
                insufficient_symbols=insufficient_symbols,
                misaligned_symbols=[]
            )
        
        report = reporter.generate_attribution_table()
        
        # Validate
        if report.get("unattributed_count", 0) > 0:
            self.failures.append(f"EV-RG-RUN-6: {report['unattributed_count']} undefined regimes lack attribution")
            report["status"] = "FAILED"
        else:
            report["status"] = "SUCCESS"
        
        # Write CSV
        csv_path = self.output_dir / "undefined_regime_attribution.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "cause", "details", "affected_symbols", "resolution_hint"])
            for attr in report.get("attributions", []):
                writer.writerow([
                    attr["timestamp"],
                    attr["cause"],
                    attr["details"],
                    "|".join(attr["affected_symbols"]),
                    attr["resolution_hint"]
                ])
        
        self.results["undefined_attribution"] = report
        print(f"  -> Output: {csv_path}")
        return report
    
    def compile_diagnostics_bundle(self) -> Dict[str, Any]:
        """EV-RG-RUN-7: Compile regime diagnostics bundle."""
        print("[EV-RG-RUN-7] Compiling regime diagnostics bundle...")
        
        bundle = {
            "report_type": "REGIME_DIAGNOSTICS_BUNDLE",
            "generated_at": self.execution_timestamp.isoformat(),
            "execution_status": "SUCCESS" if not self.failures else "FAILED",
            "failures": self.failures,
            "components": {
                name: {
                    "status": result.get("status", "UNKNOWN"),
                    "summary": self._summarize_result(name, result)
                }
                for name, result in self.results.items()
            }
        }
        
        # Write markdown bundle
        md_path = self.output_dir / "regime_diagnostics_bundle.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Regime Diagnostics Bundle\n\n")
            f.write(f"**Generated**: {self.execution_timestamp.isoformat()}\n\n")
            f.write(f"**Overall Status**: {bundle['execution_status']}\n\n")
            
            if self.failures:
                f.write("## Failures\n\n")
                for failure in self.failures:
                    f.write(f"- ❌ {failure}\n")
                f.write("\n")
            
            f.write("## Component Status\n\n")
            f.write("| Component | Status | Summary |\n")
            f.write("|:----------|:-------|:--------|\n")
            for name, comp in bundle["components"].items():
                status_icon = "✅" if comp["status"] == "SUCCESS" else "❌"
                f.write(f"| {name} | {status_icon} {comp['status']} | {comp['summary']} |\n")
            
            f.write("\n## Artifact Locations\n\n")
            f.write("| Artifact | Path |\n")
            f.write("|:---------|:-----|\n")
            f.write(f"| Symbol Matrix | `{self.output_dir}/symbol_coverage_matrix.csv` |\n")
            f.write(f"| Coverage Report | `{self.output_dir}/ingestion_coverage_report.csv` |\n")
            f.write(f"| Sufficiency Report | `{self.output_dir}/lookback_sufficiency_report.md` |\n")
            f.write(f"| Alignment Report | `{self.output_dir}/temporal_alignment_report.md` |\n")
            f.write(f"| Viability Report | `{self.output_dir}/state_viability_report.md` |\n")
            f.write(f"| Attribution Table | `{self.output_dir}/undefined_regime_attribution.csv` |\n")
            
            f.write("\n## Next Steps\n\n")
            if self.failures:
                f.write("1. Review failures above\n")
                f.write("2. Address data gaps via ingestion\n")
                f.write("3. Re-run audit after ingestion update\n")
            else:
                f.write("1. All audits passed\n")
                f.write("2. Regime logic tuning is eligible (pending authorization)\n")
        
        print(f"  -> Output: {md_path}")
        return bundle
    
    def _summarize_result(self, name: str, result: Dict[str, Any]) -> str:
        """Generate a brief summary for a result."""
        if name == "symbol_enumeration":
            return f"{result.get('total_symbols', 0)} symbols enumerated"
        elif name == "ingestion_coverage":
            return f"Present: {result.get('present', 0)}, Missing: {result.get('missing', 0)}"
        elif name == "depth_audit":
            return f"Sufficient: {result.get('sufficient', 0)}, Insufficient: {result.get('insufficient', 0)}"
        elif name == "alignment_audit":
            return f"Aligned: {result.get('aligned_pairs', 0)}, Misaligned: {result.get('misaligned_pairs', 0)}"
        elif name == "viability_check":
            return result.get("overall_status", "UNKNOWN")
        elif name == "undefined_attribution":
            return f"{result.get('total_undefined_count', 0)} undefined attributed"
        return "See details"
    
    def run_all(self) -> Dict[str, Any]:
        """Execute all regime audit tasks in sequence."""
        print("=" * 60)
        print("REGIME AUDIT EXECUTION")
        print("=" * 60)
        print(f"Timestamp: {self.execution_timestamp.isoformat()}")
        print(f"Output Directory: {self.output_dir}")
        print("=" * 60)
        
        self.run_symbol_enumeration()
        self.run_ingestion_coverage()
        self.run_depth_audit()
        self.run_alignment_audit()
        self.run_viability_check()
        self.run_undefined_attribution()
        bundle = self.compile_diagnostics_bundle()
        
        print("=" * 60)
        print(f"EXECUTION COMPLETE: {bundle['execution_status']}")
        if self.failures:
            print(f"FAILURES: {len(self.failures)}")
            for f in self.failures:
                print(f"  - {f}")
        print("=" * 60)
        
        return bundle


# timedelta already imported at top


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Regime Observability Audit")
    parser.add_argument("--output-dir", default="docs/diagnostics/regime", help="Output directory")
    args = parser.parse_args()
    
    runner = RegimeAuditRunner(output_dir=args.output_dir)
    result = runner.run_all()
    
    # Exit with error code if failures
    sys.exit(0 if result["execution_status"] == "SUCCESS" else 1)
