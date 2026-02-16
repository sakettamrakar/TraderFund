"""
Playwright Runner — Headless Visual Capture
=============================================
Launches headless Chromium, navigates to the configured BASE_URL,
waits for DOM content loaded, and captures:
  - Full page screenshot (PNG)
  - HTML snapshot (raw DOM)
  - Console log entries

Requires: playwright (pip install playwright && playwright install chromium)

Gracefully skips if the server is not running or playwright is not installed.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from automation.automation_config import config

logger = logging.getLogger(__name__)


@dataclass
class CaptureResult:
    """Result of a visual capture session."""
    success: bool
    screenshot_path: Optional[str] = None
    html_snapshot: str = ""
    console_logs: List[str] = field(default_factory=list)
    error: Optional[str] = None


def capture_page(output_dir: str, url: Optional[str] = None) -> CaptureResult:
    """
    Launch headless Chromium, navigate to BASE_URL, and capture visual state.

    Parameters
    ----------
    output_dir : str
        Directory to save screenshot and HTML snapshot.
    url : str, optional
        Override URL (defaults to config.base_url).

    Returns
    -------
    CaptureResult with screenshot path, HTML, and console logs.
    """
    target_url = url or config.base_url
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        msg = "playwright not installed — visual capture skipped"
        logger.warning(msg)
        return CaptureResult(success=False, error=msg)

    console_entries: List[str] = []
    screenshot_path = str(out / "screenshot.png")
    html_path = out / "html_snapshot.html"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Collect console output
            page.on("console", lambda msg: console_entries.append(
                f"[{msg.type}] {msg.text}"
            ))

            # Navigate and wait for DOM content loaded
            response = page.goto(target_url, wait_until="domcontentloaded", timeout=15000)

            if response is None or response.status >= 400:
                status = response.status if response else "no response"
                msg = f"Page returned HTTP {status}"
                logger.warning(msg)
                browser.close()
                return CaptureResult(success=False, error=msg)

            # Allow rendering to settle
            page.wait_for_timeout(1000)

            # Full page screenshot
            page.screenshot(path=screenshot_path, full_page=True)

            # HTML snapshot
            html_content = page.content()
            html_path.write_text(html_content, encoding="utf-8")

            browser.close()

        logger.info(f"Visual capture complete: {screenshot_path}")
        return CaptureResult(
            success=True,
            screenshot_path=screenshot_path,
            html_snapshot=html_content,
            console_logs=console_entries,
        )

    except Exception as e:
        msg = f"Visual capture failed: {e}"
        logger.warning(msg)
        return CaptureResult(success=False, error=msg)
