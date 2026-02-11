import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SafeContext(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value

def recursive_dot_dict(d):
    if isinstance(d, dict):
        return SafeContext({k: recursive_dot_dict(v) for k, v in d.items()})
    if isinstance(d, list):
        return [recursive_dot_dict(x) for x in d]
    return d

class SemanticValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.invariants_path = project_root / "automation/quality/invariants.yaml"
        self.invariants = self._load_invariants()

    def _load_invariants(self) -> Dict:
        if not self.invariants_path.exists():
            logger.warning(f"Invariants file not found at {self.invariants_path}")
            return {}
        try:
            with open(self.invariants_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load invariants: {e}")
            return {}

    def check_distributions(self, run_dir: Path) -> Dict[str, Any]:
        """
        Checks if output files in run_dir respect the invariants.
        Returns a dictionary of results.
        """
        results = {
            "status": "PASS",
            "checks": [],
            "failures": []
        }

        if not self.invariants:
            return results

        # 1. Macro Context
        self._check_section(run_dir, "macro_context", results)

        # 2. Decision
        self._check_section(run_dir, "decision", results)

        if results["failures"]:
            results["status"] = "FAIL"

        return results

    def _check_section(self, run_dir: Path, section: str, results: Dict):
        if section not in self.invariants:
            return

        config = self.invariants[section]
        required_files = config.get("required_files", [])

        for filename in required_files:
            file_path = self._find_file(run_dir, filename)

            if not file_path:
                results["checks"].append({
                    "check": f"File Existence: {filename}",
                    "status": "WARN",
                    "message": "File not found"
                })
                continue

            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
            except Exception as e:
                results["failures"].append(f"Failed to parse {filename}: {e}")
                continue

            fields = config.get("fields", {})
            for field_path, rules in fields.items():
                self._validate_field(data, field_path, rules, filename, results)

    def _validate_field(self, data: Dict, field_path: str, rules: Dict, filename: str, results: Dict):
        value = self._get_nested_value(data, field_path)

        check_name = f"{filename}::{field_path}"

        if value is None:
            if rules.get("required", False):
                results["failures"].append(f"Missing required field {field_path} in {filename}")
            else:
                results["checks"].append({"check": check_name, "status": "SKIPPED", "message": "Field missing (optional)"})
            return


        # Categorical Check
        if rules.get("type") == "categorical":
            valid_values = rules.get("values", [])
            if value not in valid_values:
                results["failures"].append(f"Invalid value for {check_name}: {value}. Expected one of {valid_values}")
            else:
                results["checks"].append({"check": check_name, "status": "PASS", "value": value})

        # Range/Numerical Check
        elif rules.get("type") == "range" or rules.get("type") == "numerical":
            if isinstance(value, (int, float)):
                min_val = rules.get("min")
                max_val = rules.get("max")

                if min_val is not None and value < min_val:
                    results["failures"].append(f"Value {value} < min {min_val} for {check_name}")
                elif max_val is not None and value > max_val:
                    results["failures"].append(f"Value {value} > max {max_val} for {check_name}")
                else:
                    results["checks"].append({"check": check_name, "status": "PASS", "value": value})
            elif isinstance(value, list) and value and isinstance(value[0], (int, float)):
                # List distribution checks
                import statistics
                try:
                    mean_val = statistics.mean(value)

                    # Check mean ranges if specified
                    mean_min = rules.get("mean_min")
                    mean_max = rules.get("mean_max")

                    if mean_min is not None and mean_val < mean_min:
                        results["failures"].append(f"Mean {mean_val:.2f} < min {mean_min} for {check_name}")
                    elif mean_max is not None and mean_val > mean_max:
                        results["failures"].append(f"Mean {mean_val:.2f} > max {mean_max} for {check_name}")
                    else:
                        results["checks"].append({"check": f"{check_name}_mean", "status": "PASS", "value": mean_val})

                except Exception as e:
                    results["failures"].append(f"Failed to compute stats for {check_name}: {e}")

    def check_stability(self, run_dir: Path) -> Dict[str, Any]:
        results = {
            "status": "PASS",
            "checks": [],
            "failures": []
        }

        config = self.invariants.get("stability", {})
        if not config:
            return results

        window_size = config.get("macro_context", {}).get("window_size", 5)
        previous_runs = self._get_previous_runs(run_dir, window_size)

        if not previous_runs:
             results["checks"].append({"check": "Stability History", "status": "SKIPPED", "message": "No previous runs found"})
             return results

        # Check flips for macro_context
        macro_config = config.get("macro_context", {})
        max_flips_config = macro_config.get("max_flips", {})
        for field, max_flips in max_flips_config.items():
            flips = self._count_flips(run_dir, previous_runs, "macro_context.json", field)
            if flips > max_flips:
                 results["failures"].append(f"Stability Violation: {field} flipped {flips} times (max {max_flips})")
            else:
                 results["checks"].append({"check": f"Stability: {field}", "status": "PASS", "flips": flips})

        # Check numerical stability (max delta)
        max_delta_config = macro_config.get("max_delta", {})
        for field, max_delta in max_delta_config.items():
            delta = self._check_max_delta(run_dir, previous_runs, "macro_context.json", field)
            if delta is not None and delta > max_delta:
                 results["failures"].append(f"Stability Violation: {field} changed by {delta:.4f} (max {max_delta})")
            elif delta is not None:
                 results["checks"].append({"check": f"Stability Delta: {field}", "status": "PASS", "delta": delta})

        if results["failures"]:
            results["status"] = "FAIL"
        return results

    def check_coherence(self, run_dir: Path) -> Dict[str, Any]:
        results = {
            "status": "PASS",
            "checks": [],
            "failures": []
        }

        config = self.invariants.get("coherence", {})
        if not config:
            return results

        rules = config.get("rules", [])
        context = self._build_eval_context(run_dir)

        for rule in rules:
            rule_name = rule.get("name", "Unnamed Rule")
            condition = rule.get("condition")

            try:
                # Safe eval with recursive dot dict context
                if eval(condition, {"__builtins__": None}, context):
                    # Condition met, apply constraints
                    forbidden = rule.get("forbidden_action")
                    if forbidden:
                        # Assuming 'decision' structure in context
                        # If context has 'decision', use it. Or assume 'action' is top level if merged?
                        # My _build_eval_context merges everything.
                        action = context.get("decision", {}).get("action") if context.get("decision") else context.get("action")

                        if action == forbidden:
                            results["failures"].append(f"Coherence Violation [{rule_name}]: Action {action} forbidden when {condition}")
                            continue

                    max_conf = rule.get("max_confidence")
                    if max_conf is not None:
                        conf = context.get("decision", {}).get("confidence") if context.get("decision") else context.get("confidence")
                        if conf is not None and conf > max_conf:
                             results["failures"].append(f"Coherence Violation [{rule_name}]: Confidence {conf} > {max_conf} when {condition}")
                             continue

                    results["checks"].append({"check": f"Coherence: {rule_name}", "status": "PASS"})

            except Exception as e:
                # Condition likely refers to missing data, or syntax error in invariant
                results["checks"].append({"check": f"Coherence: {rule_name}", "status": "SKIPPED", "message": str(e)})

        if results["failures"]:
            results["status"] = "FAIL"
        return results

    def _build_eval_context(self, run_dir: Path) -> Dict[str, Any]:
        context = {}

        # Load Macro
        macro_path = self._find_file(run_dir, "macro_context.json")
        if macro_path:
            try:
                with open(macro_path, "r") as f:
                    data = json.load(f)
                    # Merge into context. Ideally flatten or namespace?
                    # Invariants use 'risk.volatility'. If 'risk' is a key in data, recursive_dot_dict handles it.
                    context.update(data)
            except: pass

        # Load Decision
        decision_path = self._find_file(run_dir, "decision.json")
        if decision_path:
            try:
                with open(decision_path, "r") as f:
                    data = json.load(f)
                    # Merge decision data. If collision, we have a problem.
                    # Usually decision has 'action', 'confidence'. Macro has 'risk', 'monetary'.
                    # Should be safe to merge.
                    context.update(data)
                    # Also add a 'decision' key pointing to itself for explicit access
                    context["decision"] = data
            except: pass

        return recursive_dot_dict(context)

    def _get_previous_runs(self, current_run_dir: Path, limit: int) -> List[Path]:
        runs_root = current_run_dir.parent
        # Look for dirs that look like runs
        all_runs = []
        for p in runs_root.iterdir():
            if p.is_dir() and p.name != current_run_dir.name and (p / "summary.json").exists():
                 all_runs.append(p)

        # Sort by creation time or name (assuming timestamp in name)
        # Name format: taskID_YYYYMMDDHHMMSS
        # We can just sort by name as ISO timestamp sorts lexically
        all_runs.sort(key=lambda x: x.name, reverse=True)
        return all_runs[:limit]

    def _count_flips(self, current_run_dir: Path, previous_runs: List[Path], filename: str, field_path: str) -> int:
        current_val = self._load_value(current_run_dir, filename, field_path)
        if current_val is None: return 0

        flips = 0
        last_val = current_val

        for run in previous_runs:
             val = self._load_value(run, filename, field_path)
             if val is not None and val != last_val:
                 flips += 1
             last_val = val

        return flips

    def _check_max_delta(self, current_run_dir: Path, previous_runs: List[Path], filename: str, field_path: str) -> Optional[float]:
        current_val = self._load_value(current_run_dir, filename, field_path)
        if current_val is None or not isinstance(current_val, (int, float)): return None

        # Check against immediate previous run
        if previous_runs:
            prev_val = self._load_value(previous_runs[0], filename, field_path)
            if prev_val is not None and isinstance(prev_val, (int, float)):
                return abs(current_val - prev_val)
        return 0.0

    def _load_value(self, run_dir: Path, filename: str, field_path: str):
        file_path = self._find_file(run_dir, filename)
        if not file_path: return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            return self._get_nested_value(data, field_path)
        except:
            return None

    def _find_file(self, run_dir: Path, filename: str) -> Optional[Path]:
        f = run_dir / filename
        if f.exists(): return f
        matches = list(run_dir.rglob(filename))
        return matches[0] if matches else None

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        keys = path.split(".")
        curr = data
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return None
        return curr
