"""
PHASE QA-1 — Jules Lifecycle & Ingestion Boundary Tests
=========================================================
Comprehensive coverage for:
  1. extract_changeset_from_session()
  2. post_jules_followup_message()
  3. poll_for_pr_after_approval()
  4. approve_jules_changeset()
  5. diff[:12000] truncation in DriftAnalyzer
  6. adapter.py payload & forbidden path enforcement

No new architecture or abstractions.  Only external I/O (HTTP, timing,
subprocess) is patched — the functions under test run real code.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── Modules under test ──────────────────────────────────────
from automation.jules_supervisor import pr_handler
from automation.jules_supervisor.pr_handler import (
    approve_jules_changeset,
    extract_changeset_from_session,
    poll_for_pr_after_approval,
    post_jules_followup_message,
)
from automation.semantic.drift_analyzer import DriftAnalyzer


# ═══════════════════════════════════════════════════════════
# 1. extract_changeset_from_session()
# ═══════════════════════════════════════════════════════════

class TestExtractChangesetFromSession:

    def _make_session(self, diff: str = "diff --git a/f b/f\n+line\n") -> dict:
        """Build a minimal valid session payload."""
        return {
            "outputs": [
                {
                    "changeSet": {
                        "gitPatch": {
                            "unidiffPatch": diff,
                            "baseCommitId": "abc123",
                            "suggestedCommitMessage": "feat: something",
                        },
                        "source": "sources/github/owner/repo",
                    }
                }
            ]
        }

    def test_valid_payload_returns_full_diff(self):
        """Standard happy path — returns diff string unchanged."""
        diff = "diff --git a/x b/x\n+new line\n"
        result = extract_changeset_from_session(self._make_session(diff))
        assert result is not None
        assert result["diff"] == diff
        assert result["base_commit"] == "abc123"
        assert result["commit_msg"] == "feat: something"
        assert result["source"] == "sources/github/owner/repo"

    def test_alternate_key_names(self):
        """Handles snake_case aliases: change_set / git_patch / patch."""
        payload = {
            "outputs": [
                {
                    "change_set": {
                        "git_patch": {
                            "patch": "diff --git a/y b/y\n+alt\n",
                            "baseCommitId": "def456",
                        }
                    }
                }
            ]
        }
        result = extract_changeset_from_session(payload)
        assert result is not None
        assert result["diff"].startswith("diff --git")

    def test_missing_changeset_returns_none_and_logs(self, caplog):
        """No changeSet in outputs → None + NO_CHANGESET warning."""
        payload = {"outputs": [{"pullRequest": {"url": "https://github.com/o/r/pull/1"}}]}
        with caplog.at_level(logging.WARNING, logger="automation.jules_supervisor.pr_handler"):
            result = extract_changeset_from_session(payload)
        assert result is None
        assert any("NO_CHANGESET" in r.message for r in caplog.records)

    def test_outputs_not_list_logs_schema_drift(self, caplog):
        """outputs is a dict instead of list → None + SCHEMA_DRIFT warning."""
        payload = {"outputs": {"unexpected": "dict"}}
        with caplog.at_level(logging.WARNING, logger="automation.jules_supervisor.pr_handler"):
            result = extract_changeset_from_session(payload)
        assert result is None
        assert any("SCHEMA_DRIFT" in r.message for r in caplog.records)

    def test_git_patch_missing_logs_schema_drift(self, caplog):
        """changeSet present but gitPatch absent → SCHEMA_DRIFT warning."""
        payload = {
            "outputs": [
                {"changeSet": {"source": "repo"}}  # no gitPatch
            ]
        }
        with caplog.at_level(logging.WARNING, logger="automation.jules_supervisor.pr_handler"):
            result = extract_changeset_from_session(payload)
        assert result is None
        assert any("SCHEMA_DRIFT" in r.message for r in caplog.records)

    def test_empty_patch_returns_none_and_logs(self, caplog):
        """gitPatch present but unidiffPatch is whitespace → EMPTY_PATCH warning."""
        payload = {
            "outputs": [
                {
                    "changeSet": {
                        "gitPatch": {
                            "unidiffPatch": "   \n  ",
                            "baseCommitId": "xyz",
                        }
                    }
                }
            ]
        }
        with caplog.at_level(logging.WARNING, logger="automation.jules_supervisor.pr_handler"):
            result = extract_changeset_from_session(payload)
        assert result is None
        assert any("EMPTY_PATCH" in r.message for r in caplog.records)

    def test_empty_outputs_list_returns_none_and_logs(self, caplog):
        """Empty outputs list → None + NO_CHANGESET warning."""
        with caplog.at_level(logging.WARNING, logger="automation.jules_supervisor.pr_handler"):
            result = extract_changeset_from_session({"outputs": []})
        assert result is None
        assert any("NO_CHANGESET" in r.message for r in caplog.records)

    def test_completely_empty_payload_returns_none(self):
        """Empty dict → None without crashing."""
        assert extract_changeset_from_session({}) is None

    def test_large_diff_returned_in_full(self):
        """Extraction must NOT truncate — it returns the full raw diff."""
        large_diff = "+" + "x" * 20_000
        result = extract_changeset_from_session(self._make_session(large_diff))
        assert result is not None
        assert len(result["diff"]) == len(large_diff)

    def test_success_logs_diff_length(self, caplog):
        """Successful extraction logs diff_len at INFO."""
        diff = "diff --git a/f b/f\n" + "+" * 500
        with caplog.at_level(logging.INFO, logger="automation.jules_supervisor.pr_handler"):
            result = extract_changeset_from_session(self._make_session(diff))
        assert result is not None
        assert any("SUCCESS" in r.message and "diff_len=" in r.message for r in caplog.records)

    def test_skips_non_dict_output_entries(self):
        """Non-dict entries in outputs list are skipped without crash."""
        payload = {
            "outputs": [
                "not a dict",
                42,
                None,
                {
                    "changeSet": {
                        "gitPatch": {"unidiffPatch": "diff --git a/a b/a\n+ok\n"}
                    }
                },
            ]
        }
        result = extract_changeset_from_session(payload)
        assert result is not None
        assert result["diff"].startswith("diff --git")

    def test_first_valid_changeset_wins(self):
        """When multiple outputs exist, first valid changeSet is returned."""
        diff_first = "diff --git a/first b/first\n+first\n"
        diff_second = "diff --git a/second b/second\n+second\n"
        payload = {
            "outputs": [
                {
                    "changeSet": {
                        "gitPatch": {"unidiffPatch": diff_first}
                    }
                },
                {
                    "changeSet": {
                        "gitPatch": {"unidiffPatch": diff_second}
                    }
                },
            ]
        }
        result = extract_changeset_from_session(payload)
        assert result["diff"] == diff_first


# ═══════════════════════════════════════════════════════════
# 2. post_jules_followup_message()
# ═══════════════════════════════════════════════════════════

class TestPostJulesFollowupMessage:

    def test_first_endpoint_success(self, monkeypatch):
        """Returns success with method set to the first endpoint tried."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: {"ok": True, "data": {"id": "msg1"}},
        )
        result = post_jules_followup_message("12345", "please fix X")
        assert result["ok"] is True
        assert "messages" in result["method"]

    def test_first_fails_second_succeeds(self, monkeypatch):
        """Falls back to second endpoint (:resume) when first fails."""
        call_log = []

        def _fake_post(path, body):
            call_log.append(path)
            if "messages" in path:
                return {"ok": False, "error": "404", "status_code": 404}
            return {"ok": True, "data": {}}

        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(pr_handler, "jules_api_post", _fake_post)

        result = post_jules_followup_message("12345", "fix it")
        assert result["ok"] is True
        assert "resume" in result["method"]
        assert len(call_log) == 2

    def test_all_endpoints_fail_returns_failure(self, monkeypatch):
        """All three endpoints fail → ok=False, explicit error message."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: {"ok": False, "error": "503"},
        )
        result = post_jules_followup_message("12345", "fix everything")
        assert result["ok"] is False
        assert result["method"] is None
        assert result["error"] and len(result["error"]) > 0

    def test_api_unavailable_returns_failure(self, monkeypatch):
        """When Jules API is not configured, returns failure immediately."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: False)
        result = post_jules_followup_message("12345", "fix it")
        assert result["ok"] is False

    def test_fix_prompt_content_is_delivered(self, monkeypatch):
        """The fix_prompt text is present in the body sent to the API."""
        captured = {}

        def _fake_post(path, body):
            captured.update(body)
            return {"ok": True, "data": {}}

        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(pr_handler, "jules_api_post", _fake_post)

        fix_prompt = "You must add logging to every trust decision."
        post_jules_followup_message("99999", fix_prompt)
        assert fix_prompt in (captured.get("content") or captured.get("prompt") or "")

    def test_session_id_with_prefix_is_handled(self, monkeypatch):
        """session_id 'sessions/12345' is parsed correctly."""
        calls = []
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: calls.append(path) or {"ok": True, "data": {}},
        )
        post_jules_followup_message("sessions/12345", "fix it")
        assert calls[0].startswith("sessions/12345/")

    def test_session_id_numeric_only_is_handled(self, monkeypatch):
        """session_id '12345' without prefix still builds the correct path."""
        calls = []
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: calls.append(path) or {"ok": True, "data": {}},
        )
        post_jules_followup_message("12345", "fix it")
        assert "12345" in calls[0]


# ═══════════════════════════════════════════════════════════
# 3. poll_for_pr_after_approval()
# ═══════════════════════════════════════════════════════════

class TestPollForPrAfterApproval:

    _PR_PAYLOAD = {
        "pr_url": "https://github.com/org/repo/pull/42",
        "branch": "feature/inv4",
        "commit_sha": "abc123",
        "created_at": "2026-02-18T00:00:00Z",
    }

    def _session_with_pr(self) -> dict:
        return {
            "ok": True,
            "data": {
                "outputs": [
                    {"pullRequest": self._PR_PAYLOAD}
                ]
            },
        }

    def test_pr_found_immediately(self, monkeypatch):
        """PR available on the first poll → returned without further retries."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(pr_handler, "jules_api_get", lambda path: self._session_with_pr())
        monkeypatch.setattr(pr_handler.time, "sleep", lambda _: None)
        monkeypatch.setattr(pr_handler.time, "monotonic", iter([0.0, 0.5]).__next__)

        result = poll_for_pr_after_approval("12345", timeout=60, poll_interval=1)
        assert result is not None
        assert result["pr_url"] == "https://github.com/org/repo/pull/42"

    def test_pr_found_after_n_polls(self, monkeypatch):
        """PR not available on first two polls, then appears on third."""
        poll_count = {"n": 0}

        def _fake_get(path):
            poll_count["n"] += 1
            if poll_count["n"] < 3:
                return {"ok": True, "data": {"state": "COMPLETED"}}
            return self._session_with_pr()

        # Provide enough monotonic values for the loop: start + each iteration check
        times = iter([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(pr_handler, "jules_api_get", _fake_get)
        monkeypatch.setattr(pr_handler.time, "sleep", lambda _: None)
        monkeypatch.setattr(pr_handler.time, "monotonic", times.__next__)

        result = poll_for_pr_after_approval("12345", timeout=60, poll_interval=1)
        assert result is not None
        assert poll_count["n"] == 3

    def test_timeout_returns_none(self, monkeypatch):
        """When deadline passes without PR, returns None."""
        # monotonic always returns a time past the deadline
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler, "jules_api_get",
            lambda path: {"ok": True, "data": {"state": "COMPLETED"}},
        )
        monkeypatch.setattr(pr_handler.time, "sleep", lambda _: None)
        # First call returns start time, all subsequent calls return past deadline
        times = iter([0.0, 200.0])
        monkeypatch.setattr(pr_handler.time, "monotonic", times.__next__)

        result = poll_for_pr_after_approval("12345", timeout=10, poll_interval=1)
        assert result is None

    def test_api_error_does_not_crash(self, monkeypatch):
        """Network errors on get are swallowed — poll continues until timeout."""
        times = iter([0.0, 1.0, 200.0])
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(pr_handler, "jules_api_get", lambda path: {"ok": False, "error": "connection error"})
        monkeypatch.setattr(pr_handler.time, "sleep", lambda _: None)
        monkeypatch.setattr(pr_handler.time, "monotonic", times.__next__)

        result = poll_for_pr_after_approval("12345", timeout=10, poll_interval=1)
        assert result is None  # timed out, but did not raise

    def test_api_unavailable_returns_none_immediately(self, monkeypatch):
        """If Jules API is not configured, returns None without polling."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: False)
        result = poll_for_pr_after_approval("12345", timeout=60, poll_interval=1)
        assert result is None

    def test_pr_url_in_session_text_is_detected(self, monkeypatch):
        """Fallback: GitHub PR URL anywhere in session JSON text is extracted."""
        times = iter([0.0, 0.5])
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_get",
            lambda path: {
                "ok": True,
                "data": {
                    "description": "See https://github.com/org/repo/pull/99 for the changes."
                },
            },
        )
        monkeypatch.setattr(pr_handler.time, "sleep", lambda _: None)
        monkeypatch.setattr(pr_handler.time, "monotonic", times.__next__)

        result = poll_for_pr_after_approval("12345", timeout=60, poll_interval=1)
        assert result is not None
        assert "pull/99" in result["pr_url"]

    def test_non_github_url_is_not_returned(self, monkeypatch):
        """Jules session URL (jules.google.com) must NOT be treated as a PR URL."""
        times = iter([0.0, 1.0, 200.0])
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_get",
            lambda path: {
                "ok": True,
                "data": {
                    "description": "Session: https://jules.google.com/session/12345/"
                },
            },
        )
        monkeypatch.setattr(pr_handler.time, "sleep", lambda _: None)
        monkeypatch.setattr(pr_handler.time, "monotonic", times.__next__)

        result = poll_for_pr_after_approval("12345", timeout=10, poll_interval=1)
        assert result is None


# ═══════════════════════════════════════════════════════════
# 4. approve_jules_changeset()
# ═══════════════════════════════════════════════════════════

class TestApproveJulesChangeset:

    def test_first_endpoint_success_with_pr_url(self, monkeypatch):
        """First :apply endpoint succeeds and returns pr_url from response."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: {
                "ok": True,
                "data": {"pr_url": "https://github.com/org/repo/pull/7"},
            },
        )
        result = approve_jules_changeset("sessions/99999")
        assert result["ok"] is True
        assert result["pr_url"] == "https://github.com/org/repo/pull/7"
        assert "apply" in result["method"]

    def test_first_endpoint_fails_fallback_to_approve(self, monkeypatch):
        """First endpoint 404 → falls back to :approve."""
        call_log = []

        def _fake_post(path, body):
            call_log.append(path)
            if "apply" in path:
                return {"ok": False, "error": "404", "status_code": 404}
            return {"ok": True, "data": {}}

        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(pr_handler, "jules_api_post", _fake_post)

        result = approve_jules_changeset("sessions/11111")
        assert result["ok"] is True
        assert "approve" in result["method"]
        assert len(call_log) == 2

    def test_all_endpoints_fail_deterministic_failure(self, monkeypatch):
        """All three endpoints fail → ok=False, no pr_url, clear error."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: {"ok": False, "error": "404"},
        )
        result = approve_jules_changeset("sessions/22222")
        assert result["ok"] is False
        assert result["pr_url"] is None
        assert result["method"] is None
        assert result["error"] and len(result["error"]) > 0

    def test_api_unavailable_returns_failure(self, monkeypatch):
        """Without API access, returns failure without crashing."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: False)
        result = approve_jules_changeset("sessions/33333")
        assert result["ok"] is False

    def test_non_github_pr_url_in_response_is_rejected(self, monkeypatch):
        """Jules session URL mistakenly returned as pr_url must be stripped."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: {
                "ok": True,
                "data": {"pr_url": "https://jules.google.com/session/12345/"},
            },
        )
        result = approve_jules_changeset("sessions/44444")
        assert result["ok"] is True
        assert result["pr_url"] is None  # rejected because not a GitHub PR URL

    def test_pr_url_from_nested_pull_request_object(self, monkeypatch):
        """Some responses nest pr_url inside pullRequest.url."""
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: {
                "ok": True,
                "data": {"pullRequest": {"url": "https://github.com/org/repo/pull/55"}},
            },
        )
        result = approve_jules_changeset("sessions/55555")
        assert result["ok"] is True
        assert result["pr_url"] == "https://github.com/org/repo/pull/55"

    def test_session_id_with_numeric_only(self, monkeypatch):
        """Numeric only session id is handled without prefixing twice."""
        calls = []
        monkeypatch.setattr(pr_handler, "jules_api_available", lambda: True)
        monkeypatch.setattr(
            pr_handler,
            "jules_api_post",
            lambda path, body: calls.append(path) or {"ok": True, "data": {}},
        )
        approve_jules_changeset("66666")
        assert "66666" in calls[0]
        assert "sessions/66666" in calls[0]


# ═══════════════════════════════════════════════════════════
# 5. diff[:12000] truncation in DriftAnalyzer
# ═══════════════════════════════════════════════════════════

class TestDriftAnalyzerTruncation:
    """Verify the 12,000-char truncation boundary in both LLM passes."""

    def _run_with_captured_prompts(self, diff: str):
        """Run dual_pass with a mocked ask() and return all captured prompts."""
        captured = []

        def _mock_ask(prompt: str) -> str:
            captured.append(prompt)
            if len(captured) == 1:
                return json.dumps({
                    "intent_match": 0.9,
                    "plan_match": 0.9,
                    "component_scope_respected": True,
                })
            return json.dumps({
                "overreach_detected": False,
                "missing_requirements": [],
                "unintended_modifications": [],
                "semantic_mismatch": [],
            })

        with patch("automation.semantic.drift_analyzer.ask", side_effect=_mock_ask):
            DriftAnalyzer().run_dual_pass(
                intent="Test intent",
                plan={"objective": "Test"},
                diff=diff,
            )
        return captured

    def test_short_diff_not_truncated(self):
        """Diff under 12000 chars passes through unchanged in both prompts."""
        diff = "+" + "x" * 500
        prompts = self._run_with_captured_prompts(diff)
        assert len(prompts) == 2
        for prompt in prompts:
            assert diff in prompt

    def test_long_diff_truncated_to_exactly_12000(self):
        """Diff over 12000 chars is truncated to exactly 12000 in each LLM prompt."""
        diff = "+" + "y" * 15_000  # 15001 chars total
        prompts = self._run_with_captured_prompts(diff)
        assert len(prompts) == 2
        expected_segment = diff[:12000]
        for prompt in prompts:
            # The truncated segment must appear in each prompt
            assert expected_segment in prompt
            # The 12001st character must NOT appear
            assert diff[12000] not in prompt.split(expected_segment, 1)[-1][:1] or \
                   prompt.count(diff[:12001]) == 0

    def test_truncation_logged_for_large_diff(self, caplog):
        """DIFF_TRUNCATED=true is logged when diff exceeds 12000 chars."""
        diff = "+" + "z" * 13_000

        def _mock_ask(prompt: str) -> str:
            if "intent_match" in prompt or len(_mock_ask.call_count_ref) == 0:
                _mock_ask.call_count_ref.append(1)
                return json.dumps({
                    "intent_match": 0.8, "plan_match": 0.8,
                    "component_scope_respected": True,
                })
            return json.dumps({
                "overreach_detected": False, "missing_requirements": [],
                "unintended_modifications": [], "semantic_mismatch": [],
            })

        _mock_ask.call_count_ref = []

        with caplog.at_level(logging.WARNING, logger="automation.semantic.drift_analyzer"):
            with patch("automation.semantic.drift_analyzer.ask", side_effect=_mock_ask):
                DriftAnalyzer().run_dual_pass(
                    intent="Intent",
                    plan={"objective": "Plan"},
                    diff=diff,
                )

        assert any("DIFF_TRUNCATED=true" in r.message for r in caplog.records)

    def test_no_truncation_log_for_short_diff(self, caplog):
        """DIFF_TRUNCATED must NOT be logged for diffs under 12000 chars."""
        diff = "+" + "a" * 100

        def _mock_ask(prompt: str) -> str:
            if not hasattr(_mock_ask, "_n"):
                _mock_ask._n = 0
            _mock_ask._n += 1
            if _mock_ask._n == 1:
                return json.dumps({
                    "intent_match": 0.9, "plan_match": 0.9,
                    "component_scope_respected": True,
                })
            return json.dumps({
                "overreach_detected": False, "missing_requirements": [],
                "unintended_modifications": [], "semantic_mismatch": [],
            })

        with caplog.at_level(logging.WARNING, logger="automation.semantic.drift_analyzer"):
            with patch("automation.semantic.drift_analyzer.ask", side_effect=_mock_ask):
                DriftAnalyzer().run_dual_pass("Intent", {"objective": "Plan"}, diff)

        assert not any("DIFF_TRUNCATED" in r.message for r in caplog.records)

    def test_diff_exactly_12000_not_truncated(self, caplog):
        """Diff at exactly 12000 chars must NOT trigger truncation log."""
        diff = "+" + "b" * 11_999  # exactly 12000 chars

        def _mock_ask(prompt: str) -> str:
            if not hasattr(_mock_ask, "_n"):
                _mock_ask._n = 0
            _mock_ask._n += 1
            if _mock_ask._n == 1:
                return json.dumps({
                    "intent_match": 0.9, "plan_match": 0.9,
                    "component_scope_respected": True,
                })
            return json.dumps({
                "overreach_detected": False, "missing_requirements": [],
                "unintended_modifications": [], "semantic_mismatch": [],
            })

        with caplog.at_level(logging.WARNING, logger="automation.semantic.drift_analyzer"):
            with patch("automation.semantic.drift_analyzer.ask", side_effect=_mock_ask):
                DriftAnalyzer().run_dual_pass("Intent", {"objective": "Plan"}, diff)

        assert not any("DIFF_TRUNCATED" in r.message for r in caplog.records)


# ═══════════════════════════════════════════════════════════
# 6. adapter.py — Payload & Forbidden Path Enforcement
# ═══════════════════════════════════════════════════════════

class TestJulesAdapterPayload:
    """
    Tests for JulesAdapter.create_job() payload integrity.

    Key invariants:
      - prompt == instructions exactly (no mutation)
      - Memory/docs files are NEVER injected into prompt
      - FORBIDDEN block passes through unchanged
      - _detect_source_name() handles edge cases gracefully
    """

    def _make_adapter(self, remote_url: str = "https://github.com/owner/repo.git"):
        from automation.jules.adapter import JulesAdapter
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=remote_url,
                stderr="",
            )
            adapter = JulesAdapter()
        return adapter

    # ── create_job() prompt pass-through ─────────────────────

    def test_prompt_equals_instructions_exactly(self):
        """create_job() must not mutate the instructions string."""
        adapter = self._make_adapter()
        instructions = "Please implement feature X in src/module.py."
        payload = adapter.create_job({"task_id": "t1", "title": "Task"}, instructions)
        assert payload["prompt"] == instructions

    def test_payload_contains_required_fields(self):
        """Payload must always have title, prompt, and sourceContext."""
        adapter = self._make_adapter()
        payload = adapter.create_job(
            {"task_id": "t1", "title": "My Task"}, "Do something."
        )
        assert "title" in payload
        assert "prompt" in payload
        assert "sourceContext" in payload
        assert payload["title"] == "My Task"
        assert "source" in payload["sourceContext"]
        assert "githubRepoContext" in payload["sourceContext"]

    def test_memory_files_not_injected_into_prompt(self):
        """Memory/epistemic paths in task dict are NOT appended to prompt."""
        adapter = self._make_adapter()
        instructions = "Implement trust scoring."
        task = {
            "task_id": "t2",
            "title": "Trust",
            "changed_memory_files": [
                "docs/memory/02_success/success_criteria.md",
                "docs/epistemic/current_phase.md",
            ],
        }
        payload = adapter.create_job(task, instructions)
        prompt = payload["prompt"]
        assert "docs/memory/" not in prompt
        assert "docs/epistemic/" not in prompt
        assert "success_criteria.md" not in prompt
        assert "current_phase.md" not in prompt

    def test_forbidden_block_in_instructions_passes_through(self):
        """If caller includes FORBIDDEN block, it is preserved verbatim in prompt."""
        adapter = self._make_adapter()
        forbidden_block = (
            "\n\nFORBIDDEN — Do NOT create, modify, or delete any files under:\n"
            "  - docs/memory/\n  - docs/epistemic/\n  - docs/\n  - .git/\n"
        )
        instructions = "Implement feature Y." + forbidden_block
        payload = adapter.create_job({"task_id": "t3", "title": "T"}, instructions)
        assert "FORBIDDEN" in payload["prompt"]
        assert "docs/memory/" in payload["prompt"]

    # ── Regression test: hidden memory injection ──────────────

    def test_regression_no_hidden_memory_injection(self):
        """
        REGRESSION GUARD: create_job() must never silently append memory file
        paths to the prompt, even if such logic is re-introduced.

        If this test fails, someone has reintroduced the memory injection bug.
        """
        adapter = self._make_adapter()
        base_instructions = "Implement logging in src/intelligence/meta_analysis.py."
        task = {
            "task_id": "reg-test",
            "title": "Anti-regression",
            # Include memory files that a re-introduced injection would pick up
            "changed_memory_files": [
                "docs/memory/02_success/success_criteria.md",
                "docs/memory/03_domain/domain_model.md",
                "docs/epistemic/current_phase.md",
            ],
            "relevant_files": [
                "docs/memory/01_intent/project_intent.md",
            ],
        }
        payload = adapter.create_job(task, base_instructions)
        prompt = payload["prompt"]

        # The prompt must start and end with exactly what was passed in
        assert prompt == base_instructions, (
            f"REGRESSION: create_job() modified the prompt.\n"
            f"Expected: {base_instructions!r}\n"
            f"Got:      {prompt!r}"
        )

    # ── _detect_source_name() edge cases ─────────────────────

    def test_detect_source_name_https_url(self):
        """Parses HTTPS GitHub remote correctly."""
        from automation.jules.adapter import JulesAdapter
        with patch("subprocess.run") as m:
            m.return_value = MagicMock(returncode=0, stdout="https://github.com/myorg/myrepo.git\n", stderr="")
            adapter = JulesAdapter()
        assert adapter.source_name == "sources/github/myorg/myrepo"

    def test_detect_source_name_ssh_url(self):
        """Parses SSH GitHub remote correctly."""
        from automation.jules.adapter import JulesAdapter
        with patch("subprocess.run") as m:
            m.return_value = MagicMock(returncode=0, stdout="git@github.com:myorg/myrepo.git\n", stderr="")
            adapter = JulesAdapter()
        assert adapter.source_name == "sources/github/myorg/myrepo"

    def test_detect_source_name_env_var_takes_priority(self):
        """JULES_SOURCE_NAME env var overrides git config detection."""
        import os
        from automation.jules.adapter import JulesAdapter
        with patch.dict(os.environ, {"JULES_SOURCE_NAME": "sources/github/custom/name"}):
            with patch("subprocess.run") as m:
                m.return_value = MagicMock(returncode=0, stdout="https://github.com/other/repo.git\n", stderr="")
                adapter = JulesAdapter()
        assert adapter.source_name == "sources/github/custom/name"

    def test_detect_source_name_fallback_on_git_error(self):
        """When git subprocess raises, falls back to default without crashing."""
        from automation.jules.adapter import JulesAdapter
        with patch("subprocess.run") as m:
            m.side_effect = FileNotFoundError("git not found")
            adapter = JulesAdapter()
        # Must not crash; returns the known fallback
        assert adapter.source_name.startswith("sources/github/")

    def test_detect_source_name_non_github_url_uses_fallback(self):
        """Non-GitHub remote URL falls back gracefully."""
        from automation.jules.adapter import JulesAdapter
        with patch("subprocess.run") as m:
            m.return_value = MagicMock(returncode=0, stdout="https://gitlab.com/org/repo.git\n", stderr="")
            adapter = JulesAdapter()
        assert adapter.source_name.startswith("sources/github/")

    def test_source_context_starting_branch_detected(self):
        """sourceContext.githubRepoContext.startingBranch is populated."""
        from automation.jules.adapter import JulesAdapter

        def _fake_run(cmd, **kwargs):
            # cmd is a list — use any() for substring matching against elements
            if any("show-current" in c for c in cmd):
                return MagicMock(returncode=0, stdout="feature/inv4\n", stderr="")
            return MagicMock(returncode=0, stdout="https://github.com/org/repo.git\n", stderr="")

        with patch("subprocess.run", side_effect=_fake_run):
            adapter = JulesAdapter()
            payload = adapter.create_job({"task_id": "t", "title": "T"}, "instr")

        assert payload["sourceContext"]["githubRepoContext"]["startingBranch"] == "feature/inv4"


# ═══════════════════════════════════════════════════════════
# 7. create_jules_task() FORBIDDEN block — Integration smoke
# ═══════════════════════════════════════════════════════════

class TestCreateJulesTaskForbiddenBlock:
    """
    verify that the instructions built by create_jules_task() always contain
    the FORBIDDEN block before being passed to JulesAdapter.create_job().
    """

    def test_forbidden_block_present_in_task_instructions(self, monkeypatch, tmp_path):
        """create_jules_task() always adds FORBIDDEN guard to instructions."""
        import automation.run_build_loop as build_loop

        captured_instructions = {}

        class _FakeJournal:
            run_id = "test-run-forbidden"

        class _FakeConfig:
            journal = _FakeJournal()

        class _CapturingAdapter:
            def create_job(self, task, instructions):
                captured_instructions["instructions"] = instructions
                return {"task_id": "x", "title": "T", "prompt": instructions,
                        "sourceContext": {"source": "s", "githubRepoContext": {"startingBranch": "main"}}}

            def submit_job(self, payload):
                return "sessions/cap-test-1"

        monkeypatch.setattr(build_loop, "JulesAdapter", _CapturingAdapter)
        monkeypatch.setattr(build_loop, "config", _FakeConfig())

        action_plan = {
            "objective": "Implement trust scoring",
            "target_files": ["src/intelligence/meta_analysis.py"],
            "detailed_instructions": ["Add logging to each trust decision."],
            "context": {
                "human_intent": {
                    "user_intent": {"goal": "Harden MetaAnalysis logging"}
                }
            },
        }

        build_loop.create_jules_task(
            changed_files=["src/intelligence/meta_analysis.py"],
            action_plan=action_plan,
        )

        instructions = captured_instructions.get("instructions", "")
        assert "FORBIDDEN" in instructions, "FORBIDDEN block must be present in Jules instructions"
        assert "docs/memory/" in instructions, "docs/memory/ must be listed as forbidden"
        assert "docs/epistemic/" in instructions, "docs/epistemic/ must be listed as forbidden"
        assert ".git/" in instructions, ".git/ must be listed as forbidden"

    def test_memory_trigger_files_excluded_from_code_targets(self, monkeypatch):
        """Memory/docs files passed as changed_files are NOT listed as code targets."""
        import automation.run_build_loop as build_loop

        captured_instructions = {}

        class _FakeJournal:
            run_id = "test-run-memory-excl"

        class _FakeConfig:
            journal = _FakeJournal()

        class _CapturingAdapter:
            def create_job(self, task, instructions):
                captured_instructions["instructions"] = instructions
                return {"task_id": "x", "title": "T", "prompt": instructions,
                        "sourceContext": {"source": "s", "githubRepoContext": {"startingBranch": "main"}}}

            def submit_job(self, payload):
                return "sessions/cap-test-2"

        monkeypatch.setattr(build_loop, "JulesAdapter", _CapturingAdapter)
        monkeypatch.setattr(build_loop, "config", _FakeConfig())

        build_loop.create_jules_task(
            changed_files=[
                "docs/memory/02_success/success_criteria.md",
                "docs/epistemic/current_phase.md",
                "src/intelligence/meta_analysis.py",
            ],
            action_plan=None,
        )

        instructions = captured_instructions.get("instructions", "")
        assert "success_criteria.md" not in instructions
        assert "current_phase.md" not in instructions
        # The code target should still appear
        assert "src/intelligence/meta_analysis.py" in instructions
