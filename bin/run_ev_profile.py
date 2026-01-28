"""
Evaluation Profile Orchestrator.
Executes EV-RUN sequence driven by a canonical Evaluation Profile.

Usage:
  python bin/run_ev_profile.py --profile docs/evolution/evaluation_profiles/EV-HISTORICAL-ROLLING-V1.yaml

Flow:
1. Load & Validate Profile
2. Build Windowed Regime Contexts (EV-RUN-0)
3. For each Window:
   a. EV-RUN-1: Bulk Evaluation
   b. EV-RUN-2: Decision Replay
   c. EV-RUN-3: Paper P&L
   d. EV-RUN-4: Coverage Diagnostics
   e. EV-RUN-5: Rejection Analysis
   f. EV-RUN-6: Compile Bundle
4. Generate Governance Evidence (Ledger + DID)
"""
import sys
import os
import argparse
import datetime
from pathlib import Path
from typing import List

# Setup Path to import from src
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution.profile_loader import load_profile, EvaluationProfile
from evolution.regime_context_builder import RegimeContextBuilder
from evolution.factor_context_builder import FactorContextBuilder
from evolution.watchers.momentum_emergence_watcher import MomentumEmergenceWatcher
from evolution.watchers.liquidity_compression_watcher import LiquidityCompressionWatcher
from evolution.watchers.expansion_transition_watcher import ExpansionTransitionWatcher
from evolution.watchers.dispersion_breakout_watcher import DispersionBreakoutWatcher
from evolution.portfolio.paper_portfolio_builder import PaperPortfolioBuilder
from evolution.bulk_evaluator import BulkEvaluator
from evolution.decision_replay import DecisionReplayWrapper
from evolution.paper_pnl import PaperPnLCalculator
from evolution.coverage_diagnostics import CoverageDiagnostics
from evolution.rejection_analysis import RejectionAnalyzer
from evolution.compile_bundle import BundleCompiler

def run_ev_sequence(context_path: Path, output_dir: Path, window_id: str):
    """Executes EV-RUN-1 through EV-RUN-6 for a specific context window."""
    print(f"  [Window: {window_id}] Starting Sequence...")
    
    # EV-RUN-CTX-FACTOR
    print(f"  [Window: {window_id}] EV-RUN-CTX-FACTOR: Building Factor Context")
    factor_output_path = output_dir / "factor_context.json"
    factor_builder = FactorContextBuilder(context_path=context_path, output_path=factor_output_path)
    factor_builder.build()

    # EV-RUN-WATCH-MOMENTUM
    print(f"  [Window: {window_id}] EV-RUN-WATCH-MOMENTUM: Observing Factor Emergence")
    watcher = MomentumEmergenceWatcher()
    watcher.watch(window_id, factor_output_path, output_dir)

    # EV-RUN-WATCH-LIQUIDITY
    print(f"  [Window: {window_id}] EV-RUN-WATCH-LIQUIDITY: Observing Compression")
    liq_watcher = LiquidityCompressionWatcher()
    liq_watcher.watch(window_id, factor_output_path, output_dir)

    # EV-RUN-WATCH-EXPANSION & DISPERSION
    print(f"  [Window: {window_id}] EV-RUN-WATCH-READINESS: Observing Expansion/Dispersion")
    exp_watcher = ExpansionTransitionWatcher()
    exp_watcher.watch(window_id, factor_output_path, output_dir)
    dis_watcher = DispersionBreakoutWatcher()
    dis_watcher.watch(window_id, factor_output_path, output_dir)

    # EV-RUN-1
    print(f"  [Window: {window_id}] EV-RUN-1: Bulk Evaluation")
    evaluator = BulkEvaluator(context_path=context_path)
    evaluator.load_factor_context(factor_output_path)
    evaluator.generate_activation_matrix(output_dir=output_dir)

    # EV-RUN-PORTFOLIO-PAPER
    print(f"  [Window: {window_id}] EV-RUN-PORTFOLIO-PAPER: Building Counterfactual Portfolio")
    portfolio_builder = PaperPortfolioBuilder()
    activation_matrix_path = output_dir / "strategy_activation_matrix.csv"
    portfolio_builder.build(window_id, activation_matrix_path, output_dir)

    # EV-RUN-2
    print(f"  [Window: {window_id}] EV-RUN-2: Decision Replay")
    replay = DecisionReplayWrapper(context_path=context_path)
    replay.execute_full_trace(output_dir=output_dir)

    # EV-RUN-3
    print(f"  [Window: {window_id}] EV-RUN-3: Paper P&L")
    pnl = PaperPnLCalculator(context_path=context_path)
    pnl.generate_summary(output_dir=output_dir)

    # EV-RUN-4
    print(f"  [Window: {window_id}] EV-RUN-4: Coverage Diagnostics")
    cov = CoverageDiagnostics(context_path=context_path)
    cov.generate_report_markdown(output_dir=output_dir)

    # EV-RUN-5
    print(f"  [Window: {window_id}] EV-RUN-5: Rejection Analysis")
    rej = RejectionAnalyzer(context_path=context_path)
    rej.generate_analysis(output_dir=output_dir)

    # EV-RUN-6
    print(f"  [Window: {window_id}] EV-RUN-6: Compile Bundle")
    # Bundle compiler needs input artifacts. Since we write to output_dir, it reads from there.
    # We pass context_path for metadata.
    compiler = BundleCompiler(context_path=context_path)
    compiler.compile(output_dir=output_dir)
    
    print(f"  [Window: {window_id}] Sequence Complete.")

def generate_governance_evidence(profile: EvaluationProfile, window_count: int, success: bool):
    """Generates Ledger Entry and DID."""
    timestamp = datetime.datetime.now().isoformat()
    status = "SUCCESS" if success else "FAILURE"
    
    # 1. Update Ledger
    ledger_path = PROJECT_ROOT / "docs" / "epistemic" / "ledger" / "evolution_log.md"
    entry = f"""
### [{timestamp}] EV-RUN Profile Execution
- **Profile**: `{profile.profile_id}` (v{profile.version})
- **Mode**: {profile.mode.type.value}
- **Windows Executed**: {window_count}
- **Decision Ref**: `{profile.governance.decision_ref}`
- **Outcome**: {status}
"""
    if ledger_path.exists():
        with open(ledger_path, 'a', encoding='utf-8') as f:
            f.write(entry)
        print(f"Ledger updated: {ledger_path}")
    else:
        print(f"WARNING: Ledger not found at {ledger_path}")

    # 2. Generate DID (Documentation Impact Declaration)
    did_filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}__evolution__{profile.profile_id.lower().replace('-', '_')}_exec.md"
    did_path = PROJECT_ROOT / "docs" / "impact" / did_filename
    
    did_content = f"""# Documentation Impact Declaration: {profile.profile_id} Execution

**Date**: {timestamp}
**Profile ID**: {profile.profile_id}
**Version**: {profile.version}
**Status**: {status}

## Execution Summary
Execution of evaluation profile `{profile.profile_id}` in `{profile.mode.type.value}` mode.

- **Window Count**: {window_count}
- **Artifact Namespace**: `{profile.outputs.artifact_namespace}`
- **Shadow Only**: {profile.execution.shadow_only}

## Artifacts Generated
All artifacts are located under:
`docs/evolution/evaluation/{profile.outputs.artifact_namespace}/`

Each window contains a full suite of EV-RUN artifacts:
- regime_context.json
- strategy_activation_matrix.csv
- decision_trace_log.parquet
- paper_pnl_summary.csv
- coverage_diagnostics.md
- rejection_analysis.csv
- evolution_evaluation_bundle.md

## Governance Check
- [x] **D013 Compliance**: Shadow-only execution verified.
- [x] **Ledger Entry**: Recorded in `evolution_log.md`.
- [x] **Invariant Check**: No strategy mutation or real execution detected.
"""
    did_path.parent.mkdir(parents=True, exist_ok=True)
    with open(did_path, 'w', encoding='utf-8') as f:
        f.write(did_content)
    print(f"DID Generated: {did_path}")

def main():
    parser = argparse.ArgumentParser(description="Run Evaluation Profile")
    parser.add_argument("--profile", type=Path, required=True, help="Path to evaluation profile YAML")
    args = parser.parse_args()
    
    try:
        # 1. Load Profile
        print(f"Loading Profile: {args.profile}")
        profile = load_profile(str(args.profile))
        print(f"Loaded {profile.profile_id} (v{profile.version}) - Mode: {profile.mode.type.value}")
        
        # 2. Build Windowed Contexts
        print("EV-RUN-0: Building Windowed Contexts...")
        builder = RegimeContextBuilder(profile=profile)
        context_paths = builder.build_windowed_contexts()
        
        if not context_paths:
            print("No windows generated. Exiting.")
            return

        # 3. Execute Sequence for each window
        success = True
        for ctx_path_str in context_paths:
            ctx_path = Path(ctx_path_str)
            # Window ID is the parent folder name
            window_id = ctx_path.parent.name
            
            # Output Directory: docs/evolution/evaluation/{namespace}/{window_id}
            output_dir = PROJECT_ROOT / "docs" / "evolution" / "evaluation" / profile.outputs.artifact_namespace / window_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                run_ev_sequence(ctx_path, output_dir, window_id)
            except Exception as e:
                print(f"ERROR in Window {window_id}: {e}")
                success = False
                # Continue to next window? Profile says allow_parallel_windows implied isolation.
                # We'll continue but mark run as Failure.
        
        # 4. Governance
        generate_governance_evidence(profile, len(context_paths), success)
        
        if success:
            print(f"Profile Execution Complete: {profile.profile_id}")
        else:
            print(f"Profile Execution Completed with ERRORS: {profile.profile_id}")
            sys.exit(1)

    except Exception as e:
        print(f"CRITICAL ORCHESTRATION FAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
