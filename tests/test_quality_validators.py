import pytest
import json
import yaml
import sys
from pathlib import Path

# Fix for pytest running in sandbox
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from automation.quality.semantic import SemanticValidator, SafeContext
from automation.quality.report import QualityReporter

@pytest.fixture
def mock_project_root(tmp_path):
    root = tmp_path

    # Create invariants file
    invariants_dir = root / "automation/quality"
    invariants_dir.mkdir(parents=True, exist_ok=True)

    invariants_data = {
        "macro_context": {
            "required_files": ["macro_context.json"],
            "fields": {
                "monetary.curve_shape": {
                    "type": "categorical",
                    "values": ["INVERTED", "FLAT", "NORMAL", "STEEP"],
                    "required": True
                },
                "risk.volatility": {
                    "type": "categorical",
                    "values": ["SUPPRESSED", "NORMAL", "ELEVATED"],
                    "required": True
                }
            }
        },
        "decision": {
            "required_files": ["decision.json"],
            "fields": {
                "confidence": {
                    "type": "range",
                    "min": 0.0,
                    "max": 1.0,
                    "required": True
                },
                "action": {
                    "type": "categorical",
                    "values": ["ENTER", "EXIT", "HOLD", "DO_NOTHING"],
                    "required": True
                }
            }
        },
        "stability": {
            "macro_context": {
                "max_flips": {
                    "monetary.curve_shape": 1
                },
                "max_delta": {
                    "monetary.ten_year": 0.5
                },
                "window_size": 3
            }
        },
        "coherence": {
            "rules": [
                {
                    "name": "Volatile_Safety",
                    "condition": "risk.volatility == 'ELEVATED'",
                    "forbidden_action": "ENTER",
                    "rationale": "Cannot enter new positions when volatility is elevated."
                }
            ]
        }
    }

    with open(invariants_dir / "invariants.yaml", "w") as f:
        yaml.dump(invariants_data, f)

    return root

def test_semantic_validator_distributions(mock_project_root):
    validator = SemanticValidator(mock_project_root)
    run_dir = mock_project_root / "runs" / "run_1"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write valid data
    with open(run_dir / "macro_context.json", "w") as f:
        json.dump({
            "monetary": {"curve_shape": "NORMAL"},
            "risk": {"volatility": "NORMAL"}
        }, f)

    with open(run_dir / "decision.json", "w") as f:
        json.dump({
            "confidence": 0.5,
            "action": "HOLD"
        }, f)

    results = validator.check_distributions(run_dir)
    assert results["status"] == "PASS"
    assert len(results["failures"]) == 0

def test_semantic_validator_distributions_failure(mock_project_root):
    validator = SemanticValidator(mock_project_root)
    run_dir = mock_project_root / "runs" / "run_fail"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write invalid data
    with open(run_dir / "macro_context.json", "w") as f:
        json.dump({
            "monetary": {"curve_shape": "INVALID_SHAPE"},
            "risk": {"volatility": "NORMAL"}
        }, f)

    results = validator.check_distributions(run_dir)
    assert results["status"] == "FAIL"
    assert any("INVALID_SHAPE" in f for f in results["failures"])

def test_semantic_validator_coherence(mock_project_root):
    validator = SemanticValidator(mock_project_root)
    run_dir = mock_project_root / "runs" / "run_coherence"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write conflicting data: High Volatility + ENTER
    with open(run_dir / "macro_context.json", "w") as f:
        json.dump({
            "monetary": {"curve_shape": "NORMAL"},
            "risk": {"volatility": "ELEVATED"}
        }, f)

    with open(run_dir / "decision.json", "w") as f:
        json.dump({
            "confidence": 0.8,
            "action": "ENTER"
        }, f)

    results = validator.check_coherence(run_dir)
    assert results["status"] == "FAIL"
    assert any("Volatile_Safety" in f for f in results["failures"])

def test_semantic_validator_stability(mock_project_root):
    validator = SemanticValidator(mock_project_root)
    runs_root = mock_project_root / "runs"

    # Previous Run 1: NORMAL
    run1 = runs_root / "run_1"
    run1.mkdir(parents=True, exist_ok=True)
    with open(run1 / "macro_context.json", "w") as f:
        json.dump({"monetary": {"curve_shape": "NORMAL"}}, f)
    with open(run1 / "summary.json", "w") as f: f.write("{}")

    # Previous Run 2: INVERTED (Flip 1)
    run2 = runs_root / "run_2"
    run2.mkdir(parents=True, exist_ok=True)
    with open(run2 / "macro_context.json", "w") as f:
        json.dump({"monetary": {"curve_shape": "INVERTED"}}, f)
    with open(run2 / "summary.json", "w") as f: f.write("{}")

    # Previous Run 3: NORMAL (Flip 2)
    run3 = runs_root / "run_3"
    run3.mkdir(parents=True, exist_ok=True)
    with open(run3 / "macro_context.json", "w") as f:
        json.dump({"monetary": {"curve_shape": "NORMAL"}}, f)
    with open(run3 / "summary.json", "w") as f: f.write("{}")

    # Current Run: INVERTED (Flip 3)
    current_run = runs_root / "run_current"
    current_run.mkdir(parents=True, exist_ok=True)
    with open(current_run / "macro_context.json", "w") as f:
        json.dump({"monetary": {"curve_shape": "INVERTED"}}, f)

    # Max flips is 1. We have lots of flipping here.
    results = validator.check_stability(current_run)
    assert results["status"] == "FAIL"
    assert any("Stability Violation" in f for f in results["failures"])

def test_semantic_validator_numerical_stability(mock_project_root):
    validator = SemanticValidator(mock_project_root)
    runs_root = mock_project_root / "runs"

    # Previous Run: 10y = 4.0
    run1 = runs_root / "run_prev"
    run1.mkdir(parents=True, exist_ok=True)
    with open(run1 / "macro_context.json", "w") as f:
        json.dump({"monetary": {"ten_year": 4.0}}, f)
    with open(run1 / "summary.json", "w") as f: f.write("{}")

    # Current Run: 10y = 5.0 (Delta 1.0 > 0.5)
    current_run = runs_root / "run_current"
    current_run.mkdir(parents=True, exist_ok=True)
    with open(current_run / "macro_context.json", "w") as f:
        json.dump({"monetary": {"ten_year": 5.0}}, f)

    results = validator.check_stability(current_run)
    assert results["status"] == "FAIL"
    assert any("ten_year changed by 1.0000" in f for f in results["failures"])


def test_semantic_validator_distribution_stats(mock_project_root):
    # Update invariants to have a numerical field
    invariants_path = mock_project_root / "automation/quality/invariants.yaml"
    with open(invariants_path, "r") as f:
        inv = yaml.safe_load(f)

    inv["macro_context"]["fields"]["monetary.rates"] = {
        "type": "numerical",
        "min": 0.0,
        "max": 10.0,
        "mean_max": 5.0
    }
    with open(invariants_path, "w") as f:
        yaml.dump(inv, f)

    validator = SemanticValidator(mock_project_root)
    run_dir = mock_project_root / "runs" / "run_stats"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write list of values. Mean = 6.0 > 5.0
    with open(run_dir / "macro_context.json", "w") as f:
        json.dump({"monetary": {"rates": [4.0, 8.0, 6.0]}}, f)

    results = validator.check_distributions(run_dir)
    assert results["status"] == "FAIL"
    assert any("Mean 6.00 > max 5.0" in f for f in results["failures"])
