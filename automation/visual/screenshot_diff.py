"""
Screenshot Diff — Pixel-Level Visual Drift Detection
======================================================
Compares the current screenshot against a baseline image.
Computes pixel difference ratio. If above threshold → visual drift.

Saves diff image to the run directory.

Requires: Pillow (pip install Pillow)

Gracefully skips if baseline doesn't exist or Pillow isn't installed.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from automation.automation_config import config

logger = logging.getLogger(__name__)

DIFF_THRESHOLD = 0.05  # 5% pixel difference = visual drift


def compare_screenshots(
    current_path: str,
    run_dir: str,
    baseline_path: Optional[str] = None,
    threshold: float = DIFF_THRESHOLD,
) -> Dict[str, Any]:
    """
    Compare current screenshot to baseline and compute pixel difference ratio.

    Parameters
    ----------
    current_path : str
        Path to the current screenshot.
    run_dir : str
        Directory to save the diff image.
    baseline_path : str, optional
        Path to baseline screenshot. Defaults to config.screenshot_baseline_path.
    threshold : float
        Pixel diff ratio above which visual_drift = True.

    Returns
    -------
    dict with:
        visual_drift: bool
        pixel_diff_ratio: float
        diff_image_path: str or None
        error: str or None
    """
    baseline = baseline_path or config.screenshot_baseline_path
    baseline_p = Path(baseline)
    current_p = Path(current_path)

    if not baseline_p.exists():
        msg = f"No baseline screenshot at {baseline} — saving current as baseline"
        logger.info(msg)
        # First run: copy current as baseline
        try:
            baseline_p.parent.mkdir(parents=True, exist_ok=True)
            baseline_p.write_bytes(current_p.read_bytes())
        except Exception as e:
            logger.warning(f"Failed to save baseline: {e}")
        return {
            "visual_drift": False,
            "pixel_diff_ratio": 0.0,
            "diff_image_path": None,
            "error": msg,
        }

    if not current_p.exists():
        msg = f"Current screenshot not found: {current_path}"
        logger.warning(msg)
        return {
            "visual_drift": False,
            "pixel_diff_ratio": 0.0,
            "diff_image_path": None,
            "error": msg,
        }

    try:
        from PIL import Image, ImageChops
    except ImportError:
        msg = "Pillow not installed — screenshot diff skipped"
        logger.warning(msg)
        return {
            "visual_drift": False,
            "pixel_diff_ratio": 0.0,
            "diff_image_path": None,
            "error": msg,
        }

    try:
        baseline_img = Image.open(str(baseline_p)).convert("RGB")
        current_img = Image.open(str(current_p)).convert("RGB")

        # Resize current to match baseline if dimensions differ
        if baseline_img.size != current_img.size:
            current_img = current_img.resize(baseline_img.size, Image.LANCZOS)

        # Compute pixel-level difference
        diff_img = ImageChops.difference(baseline_img, current_img)

        # Count differing pixels (any channel difference > 0)
        diff_data = diff_img.getdata()
        total_pixels = len(diff_data)
        changed_pixels = sum(1 for pixel in diff_data if any(c > 10 for c in pixel))

        pixel_diff_ratio = changed_pixels / total_pixels if total_pixels > 0 else 0.0
        visual_drift = pixel_diff_ratio > threshold

        # Save diff image
        diff_image_path = None
        if visual_drift:
            out_dir = Path(run_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            diff_path = out_dir / "visual_diff.png"
            diff_img.save(str(diff_path))
            diff_image_path = str(diff_path)
            logger.warning(
                f"Visual drift detected: {pixel_diff_ratio:.4f} > {threshold}"
            )
        else:
            logger.info(
                f"Screenshot comparison passed: diff={pixel_diff_ratio:.4f} <= {threshold}"
            )

        return {
            "visual_drift": visual_drift,
            "pixel_diff_ratio": round(pixel_diff_ratio, 6),
            "diff_image_path": diff_image_path,
            "error": None,
        }

    except Exception as e:
        msg = f"Screenshot diff failed: {e}"
        logger.warning(msg)
        return {
            "visual_drift": False,
            "pixel_diff_ratio": 0.0,
            "diff_image_path": None,
            "error": msg,
        }
