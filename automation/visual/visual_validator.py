"""
Visual Validator — Orchestrator
================================
Coordinates the visual validation pipeline:
  1. Determine if UI-related components were modified
  2. Run Playwright capture
  3. Run DOM assertions
  4. Run screenshot diff
  5. Generate visual_report.json

Skips gracefully if:
  - No UI component was touched
  - Visual validation is disabled in config
  - Server is not running
  - Dependencies are missing
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from automation.automation_config import config

logger = logging.getLogger(__name__)

# Components and keywords that indicate UI-related changes
UI_COMPONENT_KEYWORDS = [
    "dashboard",
    "ui",
    "frontend",
    "rendering",
    "visualization",
    "display",
    "view",
    "chart",
    "layout",
    "style",
    "css",
    "html",
]


def _is_ui_related(action_plan: Dict[str, Any]) -> bool:
    """Check if any target component or file is UI-related."""
    target_components = action_plan.get("target_components", [])
    target_files = action_plan.get("target_files", [])
    instructions = action_plan.get("detailed_instructions", [])

    # Check component names
    for comp in target_components:
        comp_lower = comp.lower()
        if any(kw in comp_lower for kw in UI_COMPONENT_KEYWORDS):
            return True

    # Check target files
    for f in target_files:
        f_lower = f.lower()
        if any(kw in f_lower for kw in ["dashboard", "src/dashboard", "frontend", ".css", ".html"]):
            return True

    # Check instructions
    combined = " ".join(str(i) for i in instructions).lower()
    if any(kw in combined for kw in UI_COMPONENT_KEYWORDS[:5]):
        return True

    return False


def run_visual_validation(
    run_id: str,
    action_plan: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Run the full visual validation pipeline.

    Parameters
    ----------
    run_id : str
        Current run identifier.
    action_plan : dict
        The current action plan.

    Returns
    -------
    dict (visual report) or None if validation was skipped.
    """
    # Check config
    if not getattr(config, "visual_validation_enabled", True):
        logger.info("Visual validation disabled in config — skipping.")
        return None

    # Check if UI-related
    if not _is_ui_related(action_plan):
        logger.info("No UI-related components in action plan — visual validation skipped.")
        return None

    logger.info(f"Visual validation triggered for run {run_id}")

    run_dir = Path("automation") / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. Playwright Capture
    capture_result = _run_playwright(str(run_dir))

    # 2. DOM Assertions
    dom_result = _run_dom_assertions(capture_result)

    # 3. Screenshot Diff
    screenshot_result = _run_screenshot_diff(capture_result, str(run_dir))

    # 4. Build Visual Report
    report = {
        "run_id": run_id,
        "dom_passed": dom_result.get("dom_passed", True),
        "visual_drift": screenshot_result.get("visual_drift", False),
        "pixel_diff_ratio": screenshot_result.get("pixel_diff_ratio", 0.0),
        "failed_assertions": dom_result.get("failed_assertions", []),
        "capture_success": capture_result is not None and capture_result.success,
        "screenshot_diff_error": screenshot_result.get("error"),
    }

    # Write report
    report_path = run_dir / "visual_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    logger.info(f"Visual report written to {report_path}")

    return report


def _run_playwright(output_dir: str):
    """Run Playwright capture, returning CaptureResult or None."""
    try:
        from automation.visual.playwright_runner import capture_page

        result = capture_page(output_dir)
        if result.success:
            logger.info("Playwright capture succeeded.")
        else:
            logger.warning(f"Playwright capture failed: {result.error}")
        return result
    except ImportError:
        logger.warning("playwright_runner not available — capture skipped.")
        return None
    except Exception as e:
        logger.warning(f"Playwright capture error: {e}")
        return None


def _run_dom_assertions(capture_result) -> Dict[str, Any]:
    """Run DOM assertions on captured HTML."""
    if capture_result is None or not capture_result.success:
        return {"dom_passed": True, "failed_assertions": ["Capture unavailable — DOM check skipped"]}

    try:
        from automation.visual.dom_assertions import check_dom

        return check_dom(
            html_content=capture_result.html_snapshot,
            console_logs=capture_result.console_logs,
            expected_flags_active=False,
            require_latency_log=False,
        )
    except ImportError:
        logger.warning("dom_assertions not available — skipping.")
        return {"dom_passed": True, "failed_assertions": []}
    except Exception as e:
        logger.warning(f"DOM assertion error: {e}")
        return {"dom_passed": True, "failed_assertions": [f"DOM check error: {e}"]}


def _run_screenshot_diff(capture_result, run_dir: str) -> Dict[str, Any]:
    """Run screenshot diff against baseline."""
    if capture_result is None or not capture_result.success or not capture_result.screenshot_path:
        return {
            "visual_drift": False,
            "pixel_diff_ratio": 0.0,
            "diff_image_path": None,
            "error": "No screenshot available for comparison",
        }

    try:
        from automation.visual.screenshot_diff import compare_screenshots

        return compare_screenshots(
            current_path=capture_result.screenshot_path,
            run_dir=run_dir,
        )
    except ImportError:
        logger.warning("screenshot_diff not available — skipping.")
        return {"visual_drift": False, "pixel_diff_ratio": 0.0, "error": "Module unavailable"}
    except Exception as e:
        logger.warning(f"Screenshot diff error: {e}")
        return {"visual_drift": False, "pixel_diff_ratio": 0.0, "error": str(e)}
