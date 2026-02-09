"""
F5 Suppression State Orchestrator CLI.

Recomputes and persists suppression state + reason registry artifacts for
requested markets and emits audit logs for snapshots/transitions.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from governance.suppression_state import compute_suppression_for_markets


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute F5 suppression state artifacts.")
    parser.add_argument(
        "--markets",
        nargs="*",
        default=["US", "INDIA"],
        help="Markets to compute (default: US INDIA)",
    )
    args = parser.parse_args()

    results = compute_suppression_for_markets([m.upper() for m in args.markets])
    for market, payload in results.items():
        summary = payload.get("summary", {})
        print(
            f"{market}: suppression_state={summary.get('suppression_state')} "
            f"reasons={len(payload.get('registry', {}).get('reasons', []))}"
        )


if __name__ == "__main__":
    main()

