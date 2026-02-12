import pytest
from pathlib import Path
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from automation.router import TaskRouter
from automation.automation_config import config

def test_router_invariant_active():
    """Verify that when config.test_router is True, the router returns a modified reason."""
    router = TaskRouter(PROJECT_ROOT)

    # Store original state
    original_state = getattr(config, "test_router", False)

    try:
        # Set test invariant
        config.test_router = True

        # Test Case 1: No files changed (returns early)
        task_no_files = {
            "task_id": "TEST-INV-1",
            "changed_memory_files": []
        }
        executor, reason = router.route(task_no_files)
        assert "[TEST_ROUTER active]" in reason, f"Reason '{reason}' missing suffix"

        # Test Case 2: Some files (defaults to AG)
        task_files = {
            "task_id": "TEST-INV-2",
            "changed_memory_files": ["non_existent_file.md"]
        }
        executor, reason = router.route(task_files)
        assert "[TEST_ROUTER active]" in reason, f"Reason '{reason}' missing suffix"

    finally:
        # Restore state
        config.test_router = original_state

def test_router_invariant_inactive():
    """Verify that when config.test_router is False, the router behaves normally."""
    router = TaskRouter(PROJECT_ROOT)

    # Store original state
    original_state = getattr(config, "test_router", False)

    try:
        config.test_router = False

        task = {
            "task_id": "TEST-INV-OFF",
            "changed_memory_files": []
        }

        executor, reason = router.route(task)

        assert "[TEST_ROUTER active]" not in reason, f"Reason '{reason}' incorrectly contains suffix"

    finally:
        config.test_router = original_state
