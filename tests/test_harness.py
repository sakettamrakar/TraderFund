import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import subprocess
from enum import Enum

from src.harness.harness import ExecutionHarness, ExecutionMode, ExecutionResult

# Dummy classes for dependencies that are not provided from other modules.
class TaskStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"

class DummyTaskSpec:
    def __init__(self, id, command, artifacts=None, depends_on=None, blocking=True):
        self.id = id
        self.command = command
        self.artifacts = artifacts or []
        self.depends_on = depends_on or []
        self.blocking = blocking

class DummyTaskGraph:
    def __init__(self):
        self._tasks = {}

    def add_task(self, spec):
        self._tasks[spec.id] = spec

    def get_task(self, task_id):
        return self._tasks.get(task_id)

# Patch the imported TaskStatus in the harness module, as its source is not available.
@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    monkeypatch.setattr('src.harness.harness.TaskStatus', TaskStatus)

@pytest.fixture
def task_graph():
    """Fixture to create a TaskGraph with some tasks."""
    graph = DummyTaskGraph()
    graph.add_task(DummyTaskSpec(id="task1", command=["echo", "task1"], artifacts=["out1.txt"]))
    graph.add_task(DummyTaskSpec(id="task2", command=["echo", "task2"], depends_on=["task1"], artifacts=["out2.txt"]))
    graph.add_task(DummyTaskSpec(id="task3", command=["fail"], artifacts=[]))
    return graph

@pytest.fixture
def harness(task_graph):
    """Fixture to create an ExecutionHarness."""
    return ExecutionHarness(task_graph)

class TestExecutionHarness:

    def test_initialization(self, harness, task_graph):
        """Test harness is initialized correctly."""
        assert harness._graph == task_graph
        assert harness._results == {}
        assert harness._belief_layer is None
        assert harness._factor_layer is None

    def test_bind_layers_and_validate(self, harness):
        """Test binding layers and precondition validation."""
        assert not harness.validate_preconditions()

        mock_belief_layer = Mock()
        mock_factor_layer = Mock()

        harness.bind_belief_layer(mock_belief_layer)
        assert harness._belief_layer == mock_belief_layer
        assert harness.validate_preconditions()

        harness.bind_factor_layer(mock_factor_layer)
        assert harness._factor_layer == mock_factor_layer

    def test_execute_without_binding_raises_error(self, harness):
        """Test execute raises RuntimeError if belief layer is not bound."""
        with pytest.raises(RuntimeError, match="Control Plane governance not bound"):
            harness.execute(["task1"], ExecutionMode.DRY_RUN)

    def test_execute_dry_run_success(self, harness):
        """Test a successful DRY_RUN execution."""
        harness.bind_belief_layer(Mock())
        results = harness.execute(["task1"], ExecutionMode.DRY_RUN)

        assert len(results) == 1
        result = results[0]
        assert isinstance(result, ExecutionResult)
        assert result.task_id == "task1"
        assert result.status == TaskStatus.SUCCESS
        assert result.artifacts == ["out1.txt"]
        assert result.error is None

        assert "task1" in harness._results
        assert harness._results["task1"] == result

    def test_execute_dry_run_task_not_found(self, harness):
        """Test DRY_RUN with a non-existent task."""
        harness.bind_belief_layer(Mock())
        results = harness.execute(["non_existent_task"], ExecutionMode.DRY_RUN)

        assert len(results) == 1
        result = results[0]
        assert result.task_id == "non_existent_task"
        assert result.status == TaskStatus.FAILED
        assert "Task not found" in result.error

    def test_execute_dry_run_dependency_failure(self, harness):
        """Test DRY_RUN with a failed dependency."""
        harness.bind_belief_layer(Mock())

        results = harness.execute(["task2"], ExecutionMode.DRY_RUN)

        assert len(results) == 1
        result = results[0]
        assert result.task_id == "task2"
        assert result.status == TaskStatus.FAILED
        assert "Dependency not satisfied: task1" in result.error

    def test_execute_real_run_success(self, harness):
        """Test a successful REAL_RUN execution."""
        harness.bind_belief_layer(Mock())

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["echo", "task1"], returncode=0, stdout="task1 output", stderr=""
            )

            results = harness.execute(["task1"], ExecutionMode.REAL_RUN)

            mock_run.assert_called_once_with(
                ["echo", "task1"], capture_output=True, text=True, check=True
            )

            assert len(results) == 1
            result = results[0]
            assert result.task_id == "task1"
            assert result.status == TaskStatus.SUCCESS
            assert result.artifacts == ["out1.txt"]
            assert result.error is None

    def test_execute_real_run_failure(self, harness):
        """Test a failed REAL_RUN execution."""
        harness.bind_belief_layer(Mock())

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd=["fail"], stderr="it failed"
            )

            results = harness.execute(["task3"], ExecutionMode.REAL_RUN)

            mock_run.assert_called_once_with(
                ["fail"], capture_output=True, text=True, check=True
            )

            assert len(results) == 1
            result = results[0]
            assert result.task_id == "task3"
            assert result.status == TaskStatus.FAILED
            assert result.error == "it failed"

    def test_execute_multiple_tasks_with_dependency(self, harness):
        """Test execution of multiple tasks with dependencies."""
        harness.bind_belief_layer(Mock())

        with patch("subprocess.run", return_value=subprocess.CompletedProcess(
            args=[], returncode=0, stdout="output", stderr=""
        )) as mock_run:
            results = harness.execute(["task1", "task2"], ExecutionMode.REAL_RUN)

            assert len(results) == 2
            assert results[0].status == TaskStatus.SUCCESS
            assert results[1].status == TaskStatus.SUCCESS
            assert mock_run.call_count == 2

    def test_get_execution_report(self, harness):
        """Test generation of the execution report."""
        harness.bind_belief_layer(Mock())
        harness.execute(["task1"], ExecutionMode.DRY_RUN)
        harness.execute(["non_existent_task"], ExecutionMode.DRY_RUN)
