import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from automation.automation_config import config
from automation.executors.base_executor import BaseExecutor, ExecutionResult
from automation.executors import registry as registry_mod
from automation.router import TaskRouter


class _FakeExecutor:
    def __init__(self, name):
        self.name = name


class _FakeHuman:
    name = "HUMAN_SUPERVISED"


class DummyExecutor(BaseExecutor):
    name = "DUMMY"
    mode = "AUTONOMOUS"

    def is_available(self) -> bool:
        return True

    def execute(self, action_plan, run_context):
        return ExecutionResult(success=True, executor_name=self.name)


def test_router_priority_jules_then_gemini(monkeypatch, tmp_path):
    router = TaskRouter(tmp_path)
    monkeypatch.setattr("automation.router.get_available_autonomous_executors", lambda project_root=None: [_FakeExecutor("JULES"), _FakeExecutor("GEMINI")])
    monkeypatch.setattr("automation.router.get_human_executor", lambda project_root=None: _FakeHuman())

    old_priority = list(config.EXECUTOR_PRIORITY)
    old_human = config.HUMAN_SUPERVISED
    try:
        config.EXECUTOR_PRIORITY = ["JULES", "GEMINI"]
        config.HUMAN_SUPERVISED = False
        selected, _ = router.route({"task_id": "r1", "run_id": "r1"})
        assert selected == "JULES"
    finally:
        config.EXECUTOR_PRIORITY = old_priority
        config.HUMAN_SUPERVISED = old_human


def test_router_gemini_when_jules_unavailable(monkeypatch, tmp_path):
    router = TaskRouter(tmp_path)
    monkeypatch.setattr("automation.router.get_available_autonomous_executors", lambda project_root=None: [_FakeExecutor("GEMINI")])
    monkeypatch.setattr("automation.router.get_human_executor", lambda project_root=None: _FakeHuman())

    old_priority = list(config.EXECUTOR_PRIORITY)
    old_human = config.HUMAN_SUPERVISED
    try:
        config.EXECUTOR_PRIORITY = ["JULES", "GEMINI"]
        config.HUMAN_SUPERVISED = False
        selected, _ = router.route({"task_id": "r2", "run_id": "r2"})
        assert selected == "GEMINI"
    finally:
        config.EXECUTOR_PRIORITY = old_priority
        config.HUMAN_SUPERVISED = old_human


def test_router_raises_when_no_autonomous(monkeypatch, tmp_path):
    router = TaskRouter(tmp_path)
    monkeypatch.setattr("automation.router.get_available_autonomous_executors", lambda project_root=None: [])
    monkeypatch.setattr("automation.router.get_human_executor", lambda project_root=None: _FakeHuman())

    old_human = config.HUMAN_SUPERVISED
    try:
        config.HUMAN_SUPERVISED = False
        with pytest.raises(RuntimeError, match="No autonomous executor available"):
            router.route({"task_id": "r3", "run_id": "r3"})
    finally:
        config.HUMAN_SUPERVISED = old_human


def test_router_human_supervised_flag(monkeypatch, tmp_path):
    router = TaskRouter(tmp_path)
    monkeypatch.setattr("automation.router.get_available_autonomous_executors", lambda project_root=None: [_FakeExecutor("JULES")])
    monkeypatch.setattr("automation.router.get_human_executor", lambda project_root=None: _FakeHuman())

    old_human = config.HUMAN_SUPERVISED
    try:
        config.HUMAN_SUPERVISED = True
        selected, _ = router.route({"task_id": "r4", "run_id": "r4"})
        assert selected == "HUMAN_SUPERVISED"
    finally:
        config.HUMAN_SUPERVISED = old_human


def test_router_writes_audit_artifacts(monkeypatch, tmp_path):
    router = TaskRouter(tmp_path)
    monkeypatch.setattr("automation.router.get_available_autonomous_executors", lambda project_root=None: [_FakeExecutor("JULES")])
    monkeypatch.setattr("automation.router.get_human_executor", lambda project_root=None: _FakeHuman())

    old_human = config.HUMAN_SUPERVISED
    try:
        config.HUMAN_SUPERVISED = False
        router.route({"task_id": "r5", "run_id": "r5"})
    finally:
        config.HUMAN_SUPERVISED = old_human

    run_dir = tmp_path / "automation" / "runs" / "r5"
    assert (run_dir / "executor_used.txt").exists()
    assert (run_dir / "execution_mode.txt").exists()
    assert (run_dir / "router_decision.json").exists()


def test_registry_accepts_new_executor_without_router_changes(monkeypatch):
    original = list(registry_mod.REGISTERED_EXECUTORS)
    try:
        registry_mod.REGISTERED_EXECUTORS.append(DummyExecutor())
        available = registry_mod.get_available_autonomous_executors(project_root=PROJECT_ROOT)
        names = {executor.name for executor in available}
        assert "DUMMY" in names
    finally:
        registry_mod.REGISTERED_EXECUTORS[:] = original
