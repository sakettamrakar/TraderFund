import pytest
from pydantic import ValidationError
from src.harness.task_spec import TaskSpec, TaskStatus, validate_task_spec


class TestTaskSpecModel:
    """Tests for the TaskSpec Pydantic model."""

    def test_creation_minimal(self):
        """Test creating a TaskSpec with minimal required fields."""
        spec = TaskSpec(
            task_id="OP-1.1",
            dwbs_ref="1.1.1",
            plane="Orchestration",
            purpose="Run initial setup."
        )
        assert spec.task_id == "OP-1.1"
        assert spec.dwbs_ref == "1.1.1"
        assert spec.plane == "Orchestration"
        assert spec.purpose == "Run initial setup."
        assert spec.status == TaskStatus.ACTIVE
        assert spec.blocking is True
        assert spec.command == []
        assert spec.inputs == []
        assert spec.depends_on == []
        assert spec.artifacts == []
        assert spec.impacts == []
        assert spec.post_hooks == []
        assert spec.validator is None
        assert spec.satisfies == []

    def test_creation_full(self):
        """Test creating a TaskSpec with all fields populated."""
        spec = TaskSpec(
            task_id="OP-1.2",
            status=TaskStatus.SKIPPED,
            dwbs_ref="1.1.2",
            plane="Strategy",
            blocking=False,
            purpose="Analyze market data.",
            command=["python", "run_analysis.py"],
            inputs=["data/raw/market.csv"],
            depends_on=["OP-1.1"],
            artifacts=["data/processed/analysis.csv"],
            impacts=["docs/analysis_summary.md"],
            post_hooks=["notify_slack"],
            validator="basic_csv_validator",
            satisfies=["REQ-101"]
        )
        assert spec.status == TaskStatus.SKIPPED
        assert not spec.blocking
        assert spec.command == ["python", "run_analysis.py"]
        assert spec.depends_on == ["OP-1.1"]
        assert spec.satisfies == ["REQ-101"]
        assert spec.validator == "basic_csv_validator"

    def test_missing_required_fields(self):
        """Test Pydantic raises validation errors for missing fields."""
        with pytest.raises(ValidationError) as excinfo:
            TaskSpec(task_id="OP-1.3", plane="Control")

        errors = excinfo.value.errors()
        error_fields = {e['loc'][0] for e in errors}
        assert 'dwbs_ref' in error_fields
        assert 'purpose' in error_fields

    def test_enum_validation(self):
        """Test that status must be a valid TaskStatus enum member."""
        with pytest.raises(ValidationError):
            TaskSpec(
                task_id="T1", dwbs_ref="1", plane="P", purpose="P",
                status="INVALID_STATUS"
            )


class TestValidateTaskSpecFunction:
    """Tests for the validate_task_spec function."""

    def test_valid_spec(self):
        """Test validate_task_spec with a valid spec."""
        valid_spec = TaskSpec(
            task_id="OP-2.1",
            dwbs_ref="4.2.1",
            plane="Control",
            purpose="Verify system integrity."
        )
        assert validate_task_spec(valid_spec) is True

    def test_no_task_id(self):
        """Test validation fails if task_id is empty."""
        spec = TaskSpec(
            task_id="", dwbs_ref="4.2.1", plane="Control", purpose="Purpose without ID."
        )
        assert validate_task_spec(spec) is False

    def test_blocking_no_purpose(self):
        """Test validation fails if task is blocking but has no purpose."""
        spec = TaskSpec(
            task_id="OP-2.2", dwbs_ref="4.2.2", plane="Control", blocking=True, purpose=""
        )
        assert validate_task_spec(spec) is False

    def test_not_blocking_no_purpose(self):
        """Test validation passes if task is not blocking and has no purpose."""
        spec = TaskSpec(
            task_id="OP-2.3", dwbs_ref="4.2.3", plane="Control", blocking=False, purpose=""
        )
        assert validate_task_spec(spec) is True
