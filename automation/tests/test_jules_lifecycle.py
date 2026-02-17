import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.jules_supervisor import artifact_collector, monitor, pr_handler


def test_successful_task_lifecycle(monkeypatch, tmp_path):
    run_id = "run-success"
    task_id = "sessions/abc123"

    status_stream = [
        {"task_id": task_id, "status": "QUEUED", "last_update": "2026-01-01T00:00:00Z", "source": "API", "payload": {}},
        {"task_id": task_id, "status": "RUNNING", "last_update": "2026-01-01T00:00:10Z", "source": "API", "payload": {}},
        {"task_id": task_id, "status": "COMPLETED", "last_update": "2026-01-01T00:00:20Z", "source": "API", "payload": {}},
    ]

    def fake_status_details(_task_id):
        return status_stream.pop(0) if status_stream else {
            "task_id": _task_id,
            "status": "COMPLETED",
            "last_update": "2026-01-01T00:00:20Z",
            "source": "API",
            "payload": {},
        }

    monkeypatch.setattr(monitor, "jules_status_details", fake_status_details)
    monkeypatch.setattr(monitor, "sleep", lambda _seconds: None)

    result = monitor.wait_for_jules_task(task_id, timeout=30, poll_interval=0)
    assert result["status"] == "COMPLETED"

    def fake_api_get(_endpoint, timeout=30):
        return {
            "ok": True,
            "data": {
                "logs": "build complete",
                "diff": "diff --git a/x b/x\n+line",
                "tests": "collected 3 items\n3 passed\ncoverage: 91%",
            },
        }

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(artifact_collector, "jules_api_available", lambda: True)
    monkeypatch.setattr(artifact_collector, "jules_cli_available", lambda: False)
    monkeypatch.setattr(artifact_collector, "jules_api_get", fake_api_get)

    artifacts = artifact_collector.collect_jules_artifacts(task_id, run_id, task_status="COMPLETED")
    run_dir = tmp_path / "automation" / "runs" / run_id
    assert (run_dir / "jules_logs.txt").exists()
    assert (run_dir / "jules_diff.patch").exists()
    assert (run_dir / "jules_tests.txt").exists()
    assert (run_dir / "jules_test_summary.json").exists()
    assert artifacts["test_summary"]["tests_passed"] == 3

    monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
    monkeypatch.setattr(pr_handler, "jules_cli_available", lambda: False)
    monkeypatch.setattr(
        pr_handler,
        "jules_api_get",
        lambda endpoint: {
            "ok": endpoint.endswith("/pr"),
            "data": {
                "pr_url": "https://github.com/org/repo/pull/123",
                "branch": "feature/jules-123",
                "commit_sha": "abc1234",
                "created_at": "2026-01-01T00:10:00Z",
            },
        },
    )

    pr = pr_handler.detect_jules_pr(task_id)
    assert pr is not None
    assert pr["pr_url"].endswith("/pull/123")


def test_failed_task_no_pr_logs_captured(monkeypatch, tmp_path):
    run_id = "run-failed"
    task_id = "sessions/fail001"

    monkeypatch.setattr(
        monitor,
        "jules_status_details",
        lambda _task_id: {
            "task_id": _task_id,
            "status": "FAILED",
            "last_update": "2026-01-01T01:00:00Z",
            "source": "API",
            "payload": {},
        },
    )
    monkeypatch.setattr(monitor, "sleep", lambda _seconds: None)
    monitor_result = monitor.wait_for_jules_task(task_id, timeout=10, poll_interval=0)
    assert monitor_result["status"] == "FAILED"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(artifact_collector, "jules_api_available", lambda: True)
    monkeypatch.setattr(artifact_collector, "jules_cli_available", lambda: False)
    monkeypatch.setattr(
        artifact_collector,
        "jules_api_get",
        lambda _endpoint, timeout=30: {"ok": True, "data": {"logs": "execution failed", "tests": "1 failed"}},
    )

    artifacts = artifact_collector.collect_jules_artifacts(task_id, run_id, task_status="FAILED")
    run_dir = tmp_path / "automation" / "runs" / run_id
    assert "execution failed" in (run_dir / "jules_logs.txt").read_text(encoding="utf-8")
    assert artifacts["test_summary"]["tests_failed"] >= 1

    monkeypatch.setattr(pr_handler, "jules_api_available", lambda: False)
    monkeypatch.setattr(pr_handler, "jules_cli_available", lambda: False)
    assert pr_handler.detect_jules_pr(task_id) is None


def test_cli_fallback_when_api_unavailable(monkeypatch):
    task_id = "sessions/cli001"

    monkeypatch.setattr(monitor, "jules_api_available", lambda: False)
    monkeypatch.setattr(monitor, "jules_cli_available", lambda: True)
    monkeypatch.setattr(
        monitor,
        "run_cli_command",
        lambda _cmd, timeout=30: {"ok": True, "stdout": "status: COMPLETED", "stderr": "", "returncode": 0},
    )

    detail = monitor.jules_status_details(task_id)
    assert detail["source"] == "CLI"
    assert detail["status"] == "COMPLETED"


def test_pr_not_created(monkeypatch):
    task_id = "sessions/nopr001"
    monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
    monkeypatch.setattr(pr_handler, "jules_cli_available", lambda: False)
    monkeypatch.setattr(pr_handler, "jules_api_get", lambda _endpoint: {"ok": True, "data": {"status": "COMPLETED"}})

    assert pr_handler.detect_jules_pr(task_id) is None


def test_persist_jules_pr(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    metadata = {
        "pr_url": "https://github.com/org/repo/pull/99",
        "branch": "feature/test",
        "commit_sha": "deadbeef",
        "created_at": "2026-01-01T00:00:00Z",
    }
    path = pr_handler.persist_jules_pr("run-pr", metadata)
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    assert loaded["pr_url"].endswith("/pull/99")
