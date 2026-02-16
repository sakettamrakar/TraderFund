"""
DOM Assertions — Deterministic UI Verification
================================================
Checks the captured HTML snapshot for:
  - Existence of required selectors
  - Numeric values match expected format
  - Warning indicators when flags are active
  - Latency logs appear if invariant requires

All checks are deterministic — no LLM involvement.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Required selectors that must be present in a valid dashboard render
REQUIRED_SELECTORS = [
    {"selector": "[data-testid]", "description": "At least one test-id element"},
    {"selector": "table", "description": "Data table present"},
]

# Patterns that indicate valid numeric formatting in the DOM
NUMERIC_PATTERNS = [
    re.compile(r"\b\d+\.\d{2,4}\b"),  # e.g., 0.95, 12.3456
    re.compile(r"\b\d{1,3}(,\d{3})*\b"),  # e.g., 1,000 or 1,000,000
]

# Keywords indicating warning/flag state
WARNING_INDICATORS = ["warning", "alert", "⚠", "🚨", "critical", "flag"]

# Latency log pattern
LATENCY_PATTERN = re.compile(r"latency|duration|elapsed|ms\b|millisecond", re.IGNORECASE)


def check_dom(
    html_content: str,
    console_logs: List[str],
    expected_flags_active: bool = False,
    require_latency_log: bool = False,
) -> Dict[str, Any]:
    """
    Run deterministic DOM assertions against captured HTML and console logs.

    Parameters
    ----------
    html_content : str
        Raw HTML of the captured page.
    console_logs : list[str]
        Console log entries from the browser.
    expected_flags_active : bool
        If True, assert that warning indicators are present.
    require_latency_log : bool
        If True, assert that latency information appears in console or DOM.

    Returns
    -------
    dict with:
        dom_passed: bool
        failed_assertions: list[str]
    """
    failed: List[str] = []
    html_lower = html_content.lower() if html_content else ""

    # 1. Required selector existence (simplified: check for tag/attribute in HTML)
    for req in REQUIRED_SELECTORS:
        selector = req["selector"]
        desc = req["description"]
        if not _selector_present(html_content, selector):
            failed.append(f"Missing required element: {desc} ({selector})")

    # 2. Numeric format validation — at least some numeric data should exist
    if html_content:
        has_numeric = any(p.search(html_content) for p in NUMERIC_PATTERNS)
        if not has_numeric:
            failed.append("No properly formatted numeric values found in DOM")

    # 3. Warning indicators when flags expected
    if expected_flags_active:
        has_warning = any(w in html_lower for w in WARNING_INDICATORS)
        if not has_warning:
            failed.append(
                "Expected warning/flag indicators active but none found in DOM"
            )

    # 4. Latency log requirement
    if require_latency_log:
        combined = html_content + " ".join(console_logs)
        if not LATENCY_PATTERN.search(combined):
            failed.append(
                "Latency log required by invariant but not found in DOM or console"
            )

    dom_passed = len(failed) == 0

    if dom_passed:
        logger.info("DOM assertions passed.")
    else:
        logger.warning(f"DOM assertions failed: {len(failed)} issues")
        for f in failed:
            logger.warning(f"  - {f}")

    return {
        "dom_passed": dom_passed,
        "failed_assertions": failed,
    }


def _selector_present(html: str, selector: str) -> bool:
    """
    Simplified selector presence check in raw HTML.

    Handles:
      - Tag selectors (e.g., 'table', 'div')
      - Attribute selectors (e.g., '[data-testid]')
      - Class selectors (e.g., '.score-card')
      - ID selectors (e.g., '#dashboard')
    """
    if not html:
        return False

    if selector.startswith("[") and selector.endswith("]"):
        # Attribute selector: [data-testid]
        attr = selector[1:-1]
        return attr in html
    elif selector.startswith("."):
        # Class selector
        class_name = selector[1:]
        return f'class="{class_name}"' in html or f"class='{class_name}'" in html or f' {class_name}' in html
    elif selector.startswith("#"):
        # ID selector
        id_name = selector[1:]
        return f'id="{id_name}"' in html or f"id='{id_name}'" in html
    else:
        # Tag selector
        return f"<{selector}" in html.lower()
