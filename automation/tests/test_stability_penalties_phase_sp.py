import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import automation.history.drift_tracker as dt
from automation.automation_config import config


def _set_history_paths(monkeypatch, tmp_path):
    history_dir = tmp_path / "automation" / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(dt, "DRIFT_LEDGER_PATH", history_dir / "drift_ledger.json")
    monkeypatch.setattr(dt, "STABILITY_REPORT_PATH", history_dir / "stability_report.json")
    monkeypatch.setattr(dt, "STABILITY_STATE_PATH", history_dir / "stability_state.json")
    dt.DRIFT_LEDGER_PATH.write_text("[]", encoding="utf-8")
    return history_dir


def _append_record(
    run_id: str,
    component: str,
    semantic_score: float,
    regression_detected: bool = False,
    clean_run: bool = False,
    overreach: bool = False,
):
    dt.append_run_record(
        run_id=run_id,
        component=component,
        alignment_score=semantic_score,
        semantic_score=semantic_score,
        overreach_detected=overreach,
        missing_steps=0,
        drift_flags=["overreach"] if overreach else [],
        plan_hash=dt.compute_plan_hash({"component": component}),
        memory_hash=dt.compute_memory_hash({"run_id": run_id}),
        recommendation="ACCEPT",
        regression_detected=regression_detected,
        target_components=[component],
        regression_score_drop=0.20 if regression_detected else 0.0,
        clean_run=clean_run,
        event_type="TEST_EVENT",
    )


def test_ledger_entries_include_phase_sp_fields(monkeypatch, tmp_path):
    history_dir = _set_history_paths(monkeypatch, tmp_path)
    _append_record("run-1", "ComponentA", 0.91, regression_detected=True, clean_run=False, overreach=True)

    ledger = json.loads((history_dir / "drift_ledger.json").read_text(encoding="utf-8"))
    assert len(ledger) == 1
    rec = ledger[0]

    for key in (
        "regression_detected",
        "target_components",
        "regression_score_drop",
        "clean_run",
        "semantic_score",
    ):
        assert key in rec

    assert rec["regression_detected"] is True
    assert rec["target_components"] == ["ComponentA"]
    assert rec["clean_run"] is False
    assert rec["semantic_score"] == 0.91


def test_persistent_penalty_and_threshold_recovery(monkeypatch, tmp_path):
    _set_history_paths(monkeypatch, tmp_path)

    saved_penalty = config.REGRESSION_PENALTY_WEIGHT
    saved_threshold = config.CLEAN_RECOVERY_THRESHOLD
    saved_recovery = config.RECOVERY_WEIGHT
    try:
        config.REGRESSION_PENALTY_WEIGHT = 0.15
        config.CLEAN_RECOVERY_THRESHOLD = 3
        config.RECOVERY_WEIGHT = 0.05

        component = "ComponentA"

        # Baseline run.
        _append_record("run-base", component, 0.95, regression_detected=False, clean_run=False)
        dt.generate_stability_report()
        baseline = dt.compute_component_stability(component)

        # Regression run applies immediate penalty.
        _append_record("run-reg", component, 0.70, regression_detected=True, clean_run=False, overreach=True)
        dt.generate_stability_report()
        after_reg = dt.compute_component_stability(component)
        assert after_reg["stability_score"] < baseline["stability_score"]
        assert after_reg["regression_count"] >= 1
        assert after_reg["consecutive_clean_runs"] == 0

        # Non-clean/non-regression run should NOT recover penalty.
        _append_record("run-neutral", component, 0.95, regression_detected=False, clean_run=False)
        dt.generate_stability_report()
        after_neutral = dt.compute_component_stability(component)
        assert after_neutral["penalty_model_score"] == after_reg["penalty_model_score"]
        assert after_neutral["regression_count"] == after_reg["regression_count"]

        # Clean run streak: recovery only after threshold.
        _append_record("run-clean-1", component, 0.95, regression_detected=False, clean_run=True)
        dt.generate_stability_report()
        clean_1 = dt.compute_component_stability(component)
        assert clean_1["penalty_model_score"] == after_reg["penalty_model_score"]

        _append_record("run-clean-2", component, 0.96, regression_detected=False, clean_run=True)
        dt.generate_stability_report()
        clean_2 = dt.compute_component_stability(component)
        assert clean_2["penalty_model_score"] == after_reg["penalty_model_score"]

        _append_record("run-clean-3", component, 0.97, regression_detected=False, clean_run=True)
        dt.generate_stability_report()
        clean_3 = dt.compute_component_stability(component)
        assert clean_3["penalty_model_score"] > clean_2["penalty_model_score"]
        assert clean_3["regression_count"] <= clean_2["regression_count"]
        assert 0.0 <= clean_3["stability_score"] <= 1.0
    finally:
        config.REGRESSION_PENALTY_WEIGHT = saved_penalty
        config.CLEAN_RECOVERY_THRESHOLD = saved_threshold
        config.RECOVERY_WEIGHT = saved_recovery
