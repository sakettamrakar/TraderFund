import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import automation.merge_controller as merge_controller
from automation.semantic.regression_detector import detect_regression


def test_handle_pr_reject_closes_and_stops(monkeypatch, tmp_path):
    runs_dir = tmp_path / "automation" / "runs"
    monkeypatch.setattr(merge_controller, "RUNS_DIR", runs_dir)
    monkeypatch.setattr(
        merge_controller,
        "_run_pre_merge_semantic",
        lambda run_id, pr_info: {
            "run_id": run_id,
            "recommendation": "REVIEW",
            "final_score": 0.72,
            "drift": {},
        },
    )
    monkeypatch.setattr(merge_controller, "_close_pr", lambda pr_url, reason: {"success": True, "method": "mock"})

    calls = {"merge": 0, "followup": 0}
    monkeypatch.setattr(
        merge_controller,
        "_merge_pr",
        lambda pr_url: calls.__setitem__("merge", calls["merge"] + 1) or {"success": True},
    )
    monkeypatch.setattr(
        merge_controller,
        "spawn_followup_run",
        lambda parent_run_id: calls.__setitem__("followup", calls["followup"] + 1) or {"run_id": "x"},
    )
    monkeypatch.setattr(merge_controller, "append_run_record", lambda **kwargs: kwargs)
    monkeypatch.setattr(merge_controller, "generate_stability_report", lambda: {"ok": True})

    result = merge_controller.handle_pr_with_semantic(
        run_id="run-reject",
        pr_info={"pr_url": "https://github.com/org/repo/pull/1", "action_plan": {}},
    )

    assert result["success"] is False
    assert result["merged"] is False
    assert calls["merge"] == 0
    assert calls["followup"] == 0

    run_dir = runs_dir / "run-reject"
    assert (run_dir / "pre_merge_semantic.json").exists()
    assert (run_dir / "merge_result.json").exists()
    payload = json.loads((run_dir / "merge_result.json").read_text(encoding="utf-8"))
    assert payload["status"] == "REJECTED"


def test_handle_pr_accept_merges_and_spawns_followup(monkeypatch, tmp_path):
    runs_dir = tmp_path / "automation" / "runs"
    monkeypatch.setattr(merge_controller, "RUNS_DIR", runs_dir)
    monkeypatch.setattr(
        merge_controller,
        "_run_pre_merge_semantic",
        lambda run_id, pr_info: {
            "run_id": run_id,
            "recommendation": "ACCEPT",
            "final_score": 0.93,
            "drift": {},
        },
    )
    monkeypatch.setattr(merge_controller, "_merge_pr", lambda pr_url: {"success": True, "method": "mock"})
    monkeypatch.setattr(
        merge_controller,
        "spawn_followup_run",
        lambda parent_run_id: {"run_id": f"{parent_run_id}_follow", "success": True},
    )
    monkeypatch.setattr(merge_controller, "append_run_record", lambda **kwargs: kwargs)
    monkeypatch.setattr(merge_controller, "generate_stability_report", lambda: {"ok": True})

    result = merge_controller.handle_pr_with_semantic(
        run_id="run-accept",
        pr_info={"pr_url": "https://github.com/org/repo/pull/2", "action_plan": {}},
    )

    assert result["success"] is True
    assert result["merged"] is True
    assert result["followup_run_id"] == "run-accept_follow"

    merge_payload = json.loads((runs_dir / "run-accept" / "merge_result.json").read_text(encoding="utf-8"))
    assert merge_payload["status"] == "MERGED"


def test_spawn_followup_run_writes_artifacts_and_regression(monkeypatch, tmp_path):
    runs_dir = tmp_path / "automation" / "runs"
    parent_run_id = "run-parent"
    parent_dir = runs_dir / parent_run_id
    parent_dir.mkdir(parents=True, exist_ok=True)

    pre_merge = {
        "recommendation": "ACCEPT",
        "final_score": 0.92,
        "action_plan": {"target_components": ["ComponentA"]},
        "target_components": ["ComponentA"],
        "drift": {"overreach_detected": False},
        "intent_source": "test-intent",
    }
    (parent_dir / "pre_merge_semantic.json").write_text(json.dumps(pre_merge), encoding="utf-8")

    monkeypatch.setattr(merge_controller, "RUNS_DIR", runs_dir)
    monkeypatch.setattr(
        merge_controller,
        "_run_post_merge_semantic",
        lambda run_id, parent_run_id, pre_report: {
            "recommendation": "REVIEW",
            "final_score": 0.61,
            "drift": {"overreach_detected": True, "missing_requirements": ["x"]},
        },
    )

    ledger_calls = []
    monkeypatch.setattr(
        merge_controller,
        "append_run_record",
        lambda **kwargs: ledger_calls.append(kwargs) or kwargs,
    )
    monkeypatch.setattr(merge_controller, "generate_stability_report", lambda: {"ok": True})

    result = merge_controller.spawn_followup_run(parent_run_id=parent_run_id)
    followup_dir = runs_dir / result["run_id"]

    assert (followup_dir / "parent_run.txt").exists()
    assert (followup_dir / "trigger_type.txt").exists()
    assert (followup_dir / "post_merge_semantic.json").exists()
    assert (followup_dir / "regression_report.json").exists()
    assert ledger_calls, "Follow-up run should append explicit ledger entries."


def test_detect_regression_rules():
    pre = {"drift": {"overreach_detected": False, "missing_requirements": []}}
    post = {"drift": {"overreach_detected": True, "missing_requirements": ["a", "b"]}}
    report = detect_regression(0.9, 0.7, tolerance=0.03, pre_report=pre, post_report=post)

    assert report["regression"] is True
    assert report["post_overreach"] is True
    assert report["post_drift_flags"] > report["pre_drift_flags"]


def test_followup_failure_does_not_fail_parent(monkeypatch, tmp_path):
    runs_dir = tmp_path / "automation" / "runs"
    monkeypatch.setattr(merge_controller, "RUNS_DIR", runs_dir)
    monkeypatch.setattr(
        merge_controller,
        "_run_pre_merge_semantic",
        lambda run_id, pr_info: {
            "run_id": run_id,
            "recommendation": "ACCEPT",
            "final_score": 0.91,
            "drift": {},
        },
    )
    monkeypatch.setattr(merge_controller, "_merge_pr", lambda pr_url: {"success": True, "method": "mock"})
    monkeypatch.setattr(merge_controller, "append_run_record", lambda **kwargs: kwargs)
    monkeypatch.setattr(merge_controller, "generate_stability_report", lambda: {"ok": True})
    monkeypatch.setattr(
        merge_controller,
        "spawn_followup_run",
        lambda parent_run_id: (_ for _ in ()).throw(RuntimeError("followup crashed")),
    )

    result = merge_controller.handle_pr_with_semantic(
        run_id="run-followup-crash",
        pr_info={"pr_url": "https://github.com/org/repo/pull/3", "action_plan": {}},
    )

    assert result["success"] is True
    assert result["merged"] is True
    assert result["followup_status"] == "FAILED"
    assert "followup crashed" in (result["followup_error"] or "")

    failure_file = runs_dir / "run-followup-crash" / "followup_failure.json"
    assert failure_file.exists()
    payload = json.loads(failure_file.read_text(encoding="utf-8"))
    assert payload["status"] == "FAILED"
