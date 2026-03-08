from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional


ValidationChecker = Callable[["ValidationContext"], "ValidationResult"]


@dataclass(slots=True)
class ValidationContext:
    repo_root: str
    phase: str
    hook: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationResult:
    phase: str
    task: str
    status: str
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ValidationTask:
    phase: str
    task: str
    description: str
    checker: ValidationChecker


class ValidationEngine:
    def run_tasks(
        self,
        tasks: Iterable[ValidationTask],
        context: ValidationContext,
    ) -> List[ValidationResult]:
        results: List[ValidationResult] = []
        for task in tasks:
            try:
                result = task.checker(context)
            except Exception as exc:
                result = ValidationResult(
                    phase=task.phase,
                    task=task.task,
                    status="FAIL",
                    reason=f"validator_exception:{type(exc).__name__}",
                    details={"message": str(exc)},
                )
            results.append(result)
        return results


def pass_result(
    phase: str,
    task: str,
    reason: str = "",
    *,
    details: Optional[Dict[str, Any]] = None,
    evidence: Optional[List[str]] = None,
) -> ValidationResult:
    return ValidationResult(
        phase=phase,
        task=task,
        status="PASS",
        reason=reason,
        details=details or {},
        evidence=evidence or [],
    )


def fail_result(
    phase: str,
    task: str,
    reason: str,
    *,
    details: Optional[Dict[str, Any]] = None,
    evidence: Optional[List[str]] = None,
) -> ValidationResult:
    return ValidationResult(
        phase=phase,
        task=task,
        status="FAIL",
        reason=reason,
        details=details or {},
        evidence=evidence or [],
    )


def skip_result(
    phase: str,
    task: str,
    reason: str,
    *,
    details: Optional[Dict[str, Any]] = None,
    evidence: Optional[List[str]] = None,
) -> ValidationResult:
    return ValidationResult(
        phase=phase,
        task=task,
        status="SKIP",
        reason=reason,
        details=details or {},
        evidence=evidence or [],
    )