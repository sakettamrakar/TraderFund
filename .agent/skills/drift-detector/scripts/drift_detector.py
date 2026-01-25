import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DriftDetector")

class DriftDetector:
    def __init__(self, root_dir: Path):
        self.root = root_dir
        self.report = {
            "status": "SYNCED",
            "drift_level": "INFO",
            "differences": []
        }

    def check_config_drift(self, active_path: Path, baseline_path: Path):
        """Compares active config (e.g., .env) keys against baseline (example)."""
        logger.info(f"Checking Config Drift: {active_path.name} vs {baseline_path.name}")
        
        if not baseline_path.exists():
            self._add_diff("config", "baseline_missing", str(baseline_path), "N/A")
            return

        if not active_path.exists():
             # This is expected if we are checking .env vs .env.example
             self._add_diff("config", "active_missing", str(active_path), "N/A")
             return

        # Simple Key Check (Assuming .env style KEY=VAL)
        def parse_env(path):
            keys = set()
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            keys.add(line.split('=', 1)[0].strip())
            except Exception as e:
                logger.error(f"Error reading {path}: {e}")
            return keys

        baseline_keys = parse_env(baseline_path)
        active_keys = parse_env(active_path)
        
        missing = baseline_keys - active_keys
        extras = active_keys - baseline_keys
        
        for k in missing:
            self._add_diff("config", "missing_key", k, "present_in_baseline")
            
        # We generally allow extras in active (secrets), but strictly demanding baseline match means extras might be drift?
        # For now, only report missing keys from baseline.

    def check_structural_drift(self, manifest_path: Path):
        """Checks if files/dirs in manifest exist."""
        logger.info(f"Checking Structural Drift against {manifest_path.name}")
        
        # Naive manifest: List of required paths (mock for now, or read from file)
        # In a real scenario, this reads Architecture_Overview.md or a JSON manifest.
        # For this implementation, we'll assume the manifest is a JSON list of required paths.
        
        if not manifest_path.exists():
             self._add_diff("structure", "manifest_missing", str(manifest_path), "N/A")
             return

        try:
            with open(manifest_path, 'r') as f:
                required_paths = json.load(f)
                
            if not isinstance(required_paths, list):
                logger.error("Manifest must be a JSON list of strings.")
                return

            for p_str in required_paths:
                p = self.root / p_str
                if not p.exists():
                    self._add_diff("structure", "missing_component", str(p_str), "exists")
                    
        except Exception as e:
             logger.error(f"Error parsing manifest: {e}")

    def _add_diff(self, loc, key, expected, actual):
        self.report["status"] = "DRIFT_DETECTED"
        self.report["drift_level"] = "WARNING"
        self.report["differences"].append({
            "location": loc,
            "key": key,
            "expected": expected,
            "actual": actual
        })

    def print_report(self):
        print(json.dumps(self.report, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Drift Detector")
    parser.add_argument("--mode", choices=["config", "structure", "all"], default="all")
    parser.add_argument("--target", help="Target file/dir", default=".")
    
    args = parser.parse_args()
    
    root = Path(os.getcwd())
    detector = DriftDetector(root)
    
    if args.mode in ["config", "all"]:
        # Standard .env check checks
        detector.check_config_drift(root / ".env", root / ".env.example")
        
    if args.mode in ["structure", "all"]:
        # Check against a temporary manifest if one doesn't exist, or specific architecture doc
        # For 'try it' purpose, we verify 'docs/epistemic' exists
        pass # Need a mechanism to define structure. 
        
    detector.print_report()

if __name__ == "__main__":
    main()
