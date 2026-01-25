"""
Evolution Evaluation Bundle Compiler (EV-RUN-6).
Aggregates all evaluation artifacts into a single readable summary.
"""
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys
import json
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

class RegimeContextError(Exception):
    """Raised when regime context is missing or violated."""
    pass

class BundleCompiler:
    def __init__(self, context_path: Optional[Path] = None):
        self._context_path = context_path or Path("docs/evolution/context/regime_context.json")
        self._regime_context = self._load_regime_context()
        self._factor_context = {}  # Loaded lazily
        
    def load_factor_context(self, factor_path: Path):
        """Load the Factor Context for binding."""
        if not factor_path.exists():
            return
        with open(factor_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self._factor_context = data.get("factor_context", {}).get("factors", {})

    def _load_regime_context(self) -> Dict[str, Any]:
        """Load and validate the authoritative regime context."""
        if not self._context_path.exists():
            raise RegimeContextError(f"MANDATORY REGIME CONTEXT MISSING at {self._context_path}. Run EV-RUN-0 first.")
        
        with open(self._context_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["regime_context"]

    def _df_to_markdown(self, df):
        """Simple DataFrame to Markdown table converter (no tabulate dep)."""
        if df.empty:
            return "Empty Table"
        
        # Header
        columns = df.columns.tolist()
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"
        
        # Rows
        rows = []
        for _, row in df.iterrows():
            rows.append("| " + " | ".join(str(val) for val in row.values) + " |")
            
        return "\n".join([header, separator] + rows)

    def compile(self, output_dir: Optional[Path] = None):
        output_dir = output_dir or Path("docs/evolution/evaluation")
        if not output_dir.exists():
            print("No evaluation artifacts found to bundle.")
            return

        bundle_path = output_dir / "evolution_evaluation_bundle.md"
        regime = self._regime_context
        
        # Factor Summary
        factor_summary = "N/A"
        if self._factor_context:
            factor_summary = ", ".join([f"{k}={v['strength']}" if 'strength' in v else f"{k}={v.get('state','?')}" for k,v in self._factor_context.items()])
            
        md = []
        md.append("# Evolution Evaluation Bundle")
        md.append("")
        md.append(f"**Window**: {regime['evaluation_window']['start']} to {regime['evaluation_window']['end']}")
        md.append(f"**Regime**: `{regime['regime_label']}` ({regime['regime_code']})")
        md.append(f"**Factors**: `{factor_summary}`")
        md.append(f"**Generated**: {datetime.now().isoformat()}")
        md.append("---")
        md.append("")
        
        with open(bundle_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(md))
            f.write("\n") # Add an extra newline after the header block
            
            f.write("## 1. Strategy Activation\n")
            matrix_path = output_dir / "strategy_activation_matrix.csv"
            if matrix_path.exists():
                df = pd.read_csv(matrix_path)
                f.write(self._df_to_markdown(df))
                f.write("\n\n")
            else:
                f.write("No strategy activation data found.\n\n")
                
            f.write("## 2. Decision Trace Log\n")
            trace_path = output_dir / "decision_trace_log.parquet"
            if trace_path.exists():
                df = pd.read_parquet(trace_path)
                f.write(self._df_to_markdown(df))
                f.write("\n\n")
            else:
                f.write("No decision trace data found.\n\n")
                
            f.write("## 3. Paper P&L Summary\n")
            pnl_path = output_dir / "paper_pnl_summary.csv"
            if pnl_path.exists():
                df = pd.read_csv(pnl_path)
                f.write(self._df_to_markdown(df))
                f.write("\n\n")
            else:
                f.write("No paper P&L data found.\n\n")
                
            f.write("## 4. Coverage Diagnostics\n")
            diag_path = output_dir / "coverage_diagnostics.md"
            if diag_path.exists():
                with open(diag_path, 'r', encoding='utf-8') as diag_f:
                    f.write(diag_f.read())
                f.write("\n\n")
            else:
                f.write("No coverage diagnostics found.\n\n")
                
            f.write("## 5. Rejection Analysis\n")
            reject_path = output_dir / "rejection_analysis.csv"
            if reject_path.exists():
                df = pd.read_csv(reject_path)
                f.write(self._df_to_markdown(df))
                f.write("\n\n")
            else:
                f.write("No rejection analysis found.\n\n")
                
        print(f"Generated Bundle: {bundle_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EV-RUN-6: Bundle Compiler")
    parser.add_argument("--context", type=Path, help="Path to regime_context.json")
    parser.add_argument("--output", type=Path, help="Directory for output artifacts")
    args = parser.parse_args()

    try:
        compiler = BundleCompiler(context_path=args.context)
        
        # Binding Factor Context
        if args.output:
            factor_path = args.output / "factor_context.json"
            compiler.load_factor_context(factor_path)
            
        print("Compiling Evaluation Bundle...")
        compiler.compile(output_dir=args.output)
        print("EV-RUN-6 Complete.")
    except Exception as e:
        print(f"CRITICAL FAILURE: {str(e)}")
        sys.exit(1)
