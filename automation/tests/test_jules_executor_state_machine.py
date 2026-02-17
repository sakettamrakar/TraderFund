import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.automation_config import config
from automation.executors.jules_executor import JulesExecutor


class _FakeAdapter:
    def create_job(self, task, instructions):
        return {"task": task, "instructions": instructions}

    def submit_job(self, payload):
        return "sessions/fake-123"


def _with_policy_settings():
    return {
        "policy": getattr(config, "JULES_PR_POLICY", "WAIT_FOR_SEMANTIC"),
        "timeout": getattr(config, "JULES_POLL_TIMEOUT_SECONDS", 1200),
        "interval": getattr(config, "JULES_POLL_INTERVAL_SECONDS", 20),
        "threshold": getattr(config, "JULES_POLL_ERROR_THRESHOLD", 3),
    }


def _restore_policy_settings(saved):
    config.JULES_PR_POLICY = saved["policy"]
    config.JULES_POLL_TIMEOUT_SECONDS = saved["timeout"]
    config.JULES_POLL_INTERVAL_SECONDS = saved["interval"]
    config.JULES_POLL_ERROR_THRESHOLD = saved["threshold"]


def test_jules_executor_pr_created_wait_for_semantic(monkeypatch, tmp_path):
    saved = _with_policy_settings()
    try:
        config.JULES_PR_POLICY = "WAIT_FOR_SEMANTIC"
        config.JULES_POLL_TIMEOUT_SECONDS = 5
        config.JULES_POLL_INTERVAL_SECONDS = 1
        config.JULES_POLL_ERROR_THRESHOLD = 3

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("automation.executors.jules_executor.jules_api_available", lambda: True)
        monkeypatch.setattr("automation.executors.jules_executor.jules_cli_available", lambda: False)
        monkeypatch.setattr("automation.executors.jules_executor.JulesAdapter", _FakeAdapter)
        monkeypatch.setattr("automation.executors.jules_executor.sleep", lambda _seconds: None)
        monkeypatch.setattr(
            "automation.executors.jules_executor.collect_jules_artifacts",
            lambda task_id, run_id, task_status=None: {"task_id": task_id, "run_id": run_id, "status": task_status},
        )

        statuses = iter(
            [
                {"status": "QUEUED", "raw_status": "QUEUED", "source": "API", "error": None},
                {"status": "RUNNING", "raw_status": "RUNNING", "source": "API", "error": None},
            ]
        )
        monkeypatch.setattr(
            "automation.executors.jules_executor.jules_status_details",
            lambda _task_id: next(statuses, {"status": "RUNNING", "raw_status": "RUNNING", "source": "API", "error": None}),
        )

        pr_calls = {"count": 0}

        def _fake_detect_pr(_task_id):
            pr_calls["count"] += 1
            if pr_calls["count"] >= 2:
                return {
                    "pr_url": "https://github.com/org/repo/pull/101",
                    "branch": "feature/jules-101",
                    "commit_sha": "abc1234",
                    "created_at": "2026-01-01T00:00:00Z",
                }
            return None

        monkeypatch.setattr("automation.executors.jules_executor.detect_jules_pr", _fake_detect_pr)

        run_dir = tmp_path / "automation" / "runs" / "run-pr"
        executor = JulesExecutor(project_root=tmp_path)
        result = executor.execute(
            {"action_plan": {"objective": "Test PR path"}},
            {
                "run_id": "run-pr",
                "run_dir": str(run_dir),
                "task_id": "task-pr",
                "project_root": str(tmp_path),
            },
        )

        assert result.success is True
        assert result.lifecycle_state == "PR_CREATED"
        assert result.jules_task_id == "sessions/fake-123"
        assert result.pr_url and result.pr_url.endswith("/pull/101")

        assert (run_dir / "jules_task.json").exists()
        assert (run_dir / "jules_poll_log.json").exists()
        assert (run_dir / "jules_terminal_state.json").exists()
        assert (run_dir / "jules_pr.json").exists()

        terminal = json.loads((run_dir / "jules_terminal_state.json").read_text(encoding="utf-8"))
        assert terminal["final_state"] == "PR_CREATED"
        assert terminal["policy_used"] == "WAIT_FOR_SEMANTIC"
    finally:
        _restore_policy_settings(saved)


def test_jules_executor_timeout(monkeypatch, tmp_path):
    saved = _with_policy_settings()
    try:
        config.JULES_PR_POLICY = "WAIT_FOR_SEMANTIC"
        config.JULES_POLL_TIMEOUT_SECONDS = 1
        config.JULES_POLL_INTERVAL_SECONDS = 1
        config.JULES_POLL_ERROR_THRESHOLD = 3

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("automation.executors.jules_executor.jules_api_available", lambda: True)
        monkeypatch.setattr("automation.executors.jules_executor.jules_cli_available", lambda: False)
        monkeypatch.setattr("automation.executors.jules_executor.JulesAdapter", _FakeAdapter)
        monkeypatch.setattr("automation.executors.jules_executor.sleep", lambda _seconds: None)
        monkeypatch.setattr(
            "automation.executors.jules_executor.collect_jules_artifacts",
            lambda task_id, run_id, task_status=None: {"task_id": task_id, "run_id": run_id, "status": task_status},
        )
        monkeypatch.setattr(
            "automation.executors.jules_executor.jules_status_details",
            lambda _task_id: {"status": "RUNNING", "raw_status": "RUNNING", "source": "API", "error": None},
        )
        monkeypatch.setattr("automation.executors.jules_executor.detect_jules_pr", lambda _task_id: None)

        run_dir = tmp_path / "automation" / "runs" / "run-timeout"
        executor = JulesExecutor(project_root=tmp_path)
        result = executor.execute(
            {"action_plan": {"objective": "Timeout path"}},
            {
                "run_id": "run-timeout",
                "run_dir": str(run_dir),
                "task_id": "task-timeout",
                "project_root": str(tmp_path),
            },
        )

        assert result.success is False
        assert result.lifecycle_state == "TIMEOUT"

        terminal = json.loads((run_dir / "jules_terminal_state.json").read_text(encoding="utf-8"))
        assert terminal["final_state"] == "TIMEOUT"
    finally:
        _restore_policy_settings(saved)


def test_jules_executor_poll_error_threshold_failure(monkeypatch, tmp_path):
    saved = _with_policy_settings()
    try:
        config.JULES_PR_POLICY = "WAIT_FOR_SEMANTIC"
        config.JULES_POLL_TIMEOUT_SECONDS = 5
        config.JULES_POLL_INTERVAL_SECONDS = 1
        config.JULES_POLL_ERROR_THRESHOLD = 2

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("automation.executors.jules_executor.jules_api_available", lambda: True)
        monkeypatch.setattr("automation.executors.jules_executor.jules_cli_available", lambda: False)
        monkeypatch.setattr("automation.executors.jules_executor.JulesAdapter", _FakeAdapter)
        monkeypatch.setattr("automation.executors.jules_executor.sleep", lambda _seconds: None)
        monkeypatch.setattr(
            "automation.executors.jules_executor.collect_jules_artifacts",
            lambda task_id, run_id, task_status=None: {"task_id": task_id, "run_id": run_id, "status": task_status},
        )
        monkeypatch.setattr(
            "automation.executors.jules_executor.jules_status_details",
            lambda _task_id: {"status": "UNKNOWN", "raw_status": "UNKNOWN", "source": "API", "error": "api failure"},
        )
        monkeypatch.setattr("automation.executors.jules_executor.detect_jules_pr", lambda _task_id: None)

        run_dir = tmp_path / "automation" / "runs" / "run-poll-fail"
        executor = JulesExecutor(project_root=tmp_path)
        result = executor.execute(
            {"action_plan": {"objective": "Poll error threshold path"}},
            {
                "run_id": "run-poll-fail",
                "run_dir": str(run_dir),
                "task_id": "task-poll-fail",
                "project_root": str(tmp_path),
            },
        )

        assert result.success is False
        assert result.lifecycle_state == "FAILED"
        assert "threshold" in (result.failure_reason or "").lower()
    finally:
        _restore_policy_settings(saved)


def test_jules_executor_pr_without_branch_is_failure(monkeypatch, tmp_path):
    saved = _with_policy_settings()
    try:
        config.JULES_PR_POLICY = "WAIT_FOR_SEMANTIC"
        config.JULES_POLL_TIMEOUT_SECONDS = 5
        config.JULES_POLL_INTERVAL_SECONDS = 1
        config.JULES_POLL_ERROR_THRESHOLD = 3

        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("automation.executors.jules_executor.jules_api_available", lambda: True)
        monkeypatch.setattr("automation.executors.jules_executor.jules_cli_available", lambda: False)
        monkeypatch.setattr("automation.executors.jules_executor.JulesAdapter", _FakeAdapter)
        monkeypatch.setattr("automation.executors.jules_executor.sleep", lambda _seconds: None)
        monkeypatch.setattr(
            "automation.executors.jules_executor.collect_jules_artifacts",
            lambda task_id, run_id, task_status=None: {"task_id": task_id, "run_id": run_id, "status": task_status},
        )
        monkeypatch.setattr(
            "automation.executors.jules_executor.jules_status_details",
            lambda _task_id: {"status": "RUNNING", "raw_status": "RUNNING", "source": "API", "error": None},
        )
        monkeypatch.setattr(
            "automation.executors.jules_executor.detect_jules_pr",
            lambda _task_id: {
                "pr_url": "https://github.com/org/repo/pull/202",
                "branch": None,
                "commit_sha": "abc1234",
            },
        )

        run_dir = tmp_path / "automation" / "runs" / "run-pr-missing-branch"
        executor = JulesExecutor(project_root=tmp_path)
        result = executor.execute(
            {"action_plan": {"objective": "PR missing branch"}},
            {
                "run_id": "run-pr-missing-branch",
                "run_dir": str(run_dir),
                "task_id": "task-pr-missing-branch",
                "project_root": str(tmp_path),
            },
        )

        assert result.success is False
        assert result.lifecycle_state == "FAILED"
        assert "branch" in (result.failure_reason or "").lower()
    finally:
        _restore_policy_settings(saved)
