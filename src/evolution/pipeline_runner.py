import argparse
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evolution.profile_loader import load_profile, ModeType, WindowingType

def run_step(step_name, command):
    print(f"[{step_name}] Executing: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[{step_name}] FAILED:\n{result.stderr}")
        raise RuntimeError(f"{step_name} failed execution.")
    print(result.stdout)
    print(f"[{step_name}] COMPLETE.\n")

def run_pipeline(profile_path: Path):
    profile = load_profile(str(profile_path))
    
    print(f"Starting EV-RUN Pipeline for: {profile.profile_id}")
    
    # 1. Generate Contexts (EV-RUN-0)
    # We call regime_context_builder directly to get the list of window paths
    from evolution.regime_context_builder import RegimeContextBuilder
    builder = RegimeContextBuilder(profile=profile)
    context_paths = builder.build_windowed_contexts()
    
    print(f"Generated {len(context_paths)} window contexts.")
    
    # 2. Iterate Per Window
    for ctx_path in context_paths:
        ctx_file = Path(ctx_path)
        # Context is in docs/evolution/context/{profile_id}/{window_id}
        # We want output in docs/evolution/evaluation/{artifact_namespace}/{window_id}
        window_id = ctx_file.parent.name
        
        output_dir = Path("docs/evolution/evaluation") / profile.outputs.artifact_namespace / window_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"=== Processing Window: {window_id} -> {output_dir} ===")
        
        # EV-RUN-CTX-FACTOR: Build Factor Context
        factor_ctx_file = output_dir / "factor_context.json"
        run_step("EV-RUN-CTX-FACTOR", ["python", "src/evolution/factor_context_builder.py", "--context", str(ctx_file), "--output", str(factor_ctx_file)])

        # EV-RUN-1: Bulk Evaluator
        run_step("EV-RUN-1", ["python", "src/evolution/bulk_evaluator.py", "--context", str(ctx_file), "--output", str(output_dir)])
        
        # EV-RUN-2: Decision Replay
        run_step("EV-RUN-2", ["python", "src/evolution/decision_replay.py", "--context", str(ctx_file), "--output", str(output_dir)])
        
        # EV-RUN-3: Paper P&L
        run_step("EV-RUN-3", ["python", "src/evolution/paper_pnl.py", "--context", str(ctx_file), "--output", str(output_dir)])
        
        # EV-RUN-4: Coverage Diagnostics
        run_step("EV-RUN-4", ["python", "src/evolution/coverage_diagnostics.py", "--context", str(ctx_file), "--output", str(output_dir)])
        
        # EV-RUN-5: Rejection Analysis
        run_step("EV-RUN-5", ["python", "src/evolution/rejection_analysis.py", "--context", str(ctx_file), "--output", str(output_dir)])
        
        # EV-RUN-6: Bundle Compiler
        run_step("EV-RUN-6", ["python", "src/evolution/compile_bundle.py", "--context", str(ctx_file), "--output", str(output_dir)])
        
    print(f"EV-RUN Pipeline for {profile.profile_id} COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EV-RUN Pipeline Runner")
    parser.add_argument("profile", type=Path, help="Path to profile YAML")
    args = parser.parse_args()
    
    try:
        run_pipeline(args.profile)
    except Exception as e:
        print(f"CRITICAL PIPELINE FAILURE: {e}")
        sys.exit(1)
