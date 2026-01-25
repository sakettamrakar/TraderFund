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
    def __init__(self):
        self._regime_context = self._load_regime_context()

    def _load_regime_context(self) -> Dict[str, Any]:
        """Load and validate the authoritative regime context."""
        context_path = Path("docs/evolution/context/regime_context.json")
        if not context_path.exists():
            raise RegimeContextError("MANDATORY REGIME CONTEXT MISSING. Run EV-RUN-0 first.")
        
        with open(context_path, 'r', encoding='utf-8') as f:
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

    def compile(self):
        output_dir = Path("docs/evolution/evaluation")
        if not output_dir.exists():
            print("No evaluation artifacts found to bundle.")
            return

        bundle_path = output_dir / "evolution_evaluation_bundle.md"
        
        with open(bundle_path, 'w', encoding='utf-8') as f:
            f.write("# Evolution Evaluation Bundle\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n")
            f.write(f"**Execution Context**: {self._regime_context['regime_label']} ({self._regime_context['regime_code']})\n")
            f.write(f"**Context Version**: {self._regime_context['version']}\n\n")
            
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
    try:
        compiler = BundleCompiler()
        compiler.compile()
        print("EV-RUN-6 Complete.")
    except Exception as e:
        print(f"CRITICAL FAILURE: {str(e)}")
        sys.exit(1)
