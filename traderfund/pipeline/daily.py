"""
Canonical Daily Pipeline Entrypoint (RR-B.1 + RR-B.5)

This is the single authoritative command for the TraderFund daily cycle.
It replaces all fragmented scheduling runners by providing one explicit path
that supports fixture mode (no credentials) and live market modes.

Usage:
    python -m traderfund.pipeline.daily --market fixture          # fixture dry-run
    python -m traderfund.pipeline.daily --market fixture --dry-run # same as above
    python -m traderfund.pipeline.daily --market US               # US live (blocked until wired)

The pipeline:
    1. Resolves market mode and validates credentials
    2. Builds an artifact manifest from the canonical contract
    3. Runs ingestion validation against the manifest
    4. (Future) Runs research / intelligence stages
    5. Emits the final manifest and validation summary
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict

# Ensure repo root is on path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from traderfund.pipeline.market_modes import MarketMode, get_mode_spec, validate_credentials
from traderfund.pipeline.artifact_contract import build_manifest_for_mode, PipelineManifest
from traderfund.validation.validation_runner import ValidationRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("PipelineDaily")

MANIFEST_PATH = _REPO_ROOT / "logs" / "validation" / "pipeline_manifest.json"


def run_daily_cycle(market: str, dry_run: bool = False) -> int:
    """
    Execute the canonical daily pipeline cycle.

    Returns 0 on success, 1 on validation failure.
    """
    # ── 1. Resolve market mode ────────────────────────────────────────────
    mode_spec = get_mode_spec(market)
    effective_mode = mode_spec.mode
    logger.info(
        "Starting Daily Pipeline | market=%s | mode=%s | dry_run=%s",
        market, effective_mode.value, dry_run,
    )

    # ── 2. Credential check ───────────────────────────────────────────────
    if not mode_spec.is_fixture and not dry_run:
        missing_creds = validate_credentials(effective_mode)
        if missing_creds:
            logger.error(
                "Missing credentials for market %s: %s. "
                "Set them in .env or use --market fixture for dry-run mode.",
                market, ", ".join(missing_creds),
            )
            return 1
    elif not mode_spec.is_fixture and dry_run:
        logger.info("Dry-run requested — skipping credential check for %s", market)

    # ── 3. Build artifact manifest ────────────────────────────────────────
    logger.info("Building artifact manifest for market=%s ...", market)
    manifest = build_manifest_for_mode(market, _REPO_ROOT)

    present_count = sum(1 for e in manifest.entries if e.status == "present")
    missing_count = sum(1 for e in manifest.entries if e.status == "missing")
    logger.info(
        "Manifest built: %d present, %d missing out of %d declared artifacts",
        present_count, missing_count, len(manifest.entries),
    )

    for entry in manifest.entries:
        if entry.status == "missing":
            logger.warning(
                "  MISSING: %s (producer: %s, pattern: %s)",
                entry.artifact_id, entry.producer, entry.path,
            )

    # ── 4. Run ingestion validation ───────────────────────────────────────
    logger.info("Running ingestion validation ...")
    runner = ValidationRunner(repo_root=str(_REPO_ROOT))
    ingestion_summary = runner.run_phase(
        "ingestion",
        hook="pipeline",
        metadata={"market": market, "manifest": manifest},
    )
    manifest.validation_summaries["ingestion"] = {
        "phase": ingestion_summary["phase"],
        "hook": ingestion_summary["hook"],
        "has_failures": ingestion_summary["has_failures"],
        "result_count": len(ingestion_summary.get("results", [])),
        "pass_count": sum(1 for r in ingestion_summary.get("results", []) if r.get("status") == "PASS"),
        "fail_count": sum(1 for r in ingestion_summary.get("results", []) if r.get("status") == "FAIL"),
        "skip_count": sum(1 for r in ingestion_summary.get("results", []) if r.get("status") == "SKIP"),
    }

    if ingestion_summary["has_failures"]:
        logger.error("Ingestion validation FAILED. Review logs/validation/ingestion_pipeline_latest.json")
        # Still write manifest so the failure is inspectable
        manifest.write(MANIFEST_PATH)
        return 1

    logger.info("Ingestion validation PASSED.")

    # ── 5. (Future) Research / intelligence stages ────────────────────────
    # Placeholder for wiring research modules into the pipeline.
    # Each stage will:
    #   a) read inputs from the manifest
    #   b) produce outputs and add entries to the manifest
    #   c) run phase validation
    logger.info("Research/intelligence stages: SKIPPED (not yet wired)")

    # ── 6. Write final manifest ───────────────────────────────────────────
    manifest.write(MANIFEST_PATH)
    logger.info("Pipeline manifest written to %s", MANIFEST_PATH)

    # ── 7. Summary ────────────────────────────────────────────────────────
    summary_line = json.dumps({
        "status": "SUCCESS",
        "market": market,
        "manifest": str(MANIFEST_PATH),
        "artifacts_present": present_count,
        "artifacts_missing": missing_count,
        "validation": manifest.validation_summaries,
    }, indent=2)
    logger.info("Pipeline completed successfully.\n%s", summary_line)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TraderFund Canonical Daily Pipeline",
        epilog="Start with --market fixture to run without live credentials.",
    )
    parser.add_argument(
        "--market",
        default="fixture",
        choices=["fixture", "US", "INDIA"],
        help="Market mode (default: fixture)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip credential checks and avoid any live side effects",
    )

    args = parser.parse_args()

    # Fixture mode always implies dry-run
    dry_run = args.dry_run or args.market == "fixture"

    if not get_mode_spec(args.market).is_fixture and not dry_run:
        logger.error(
            "Live market %s is not yet wired to the canonical pipeline. "
            "Use --market fixture or --dry-run.",
            args.market,
        )
        return 1

    return run_daily_cycle(args.market, dry_run=dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
