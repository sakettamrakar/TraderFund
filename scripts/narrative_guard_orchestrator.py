"""
F3 Narrative Guard Orchestrator CLI.

Recomputes and persists narrative governance artifacts for selected markets:
- docs/intelligence/narrative_state_<MARKET>.json
- docs/audit/f3_narrative/*.jsonl
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

from governance.narrative_guard import compute_narrative_for_markets


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute F3 narrative governance artifacts.")
    parser.add_argument(
        "--markets",
        nargs="*",
        default=["US", "INDIA"],
        help="Markets to compute (default: US INDIA)",
    )
    args = parser.parse_args()

    results = compute_narrative_for_markets([m.upper() for m in args.markets])
    for market, payload in results.items():
        narrative = payload.get("narrative", {})
        print(
            f"{market}: narrative_mode={narrative.get('narrative_mode')} "
            f"diff={narrative.get('narrative_diff', {}).get('status')} "
            f"suppression_state={narrative.get('suppression_state')}"
        )


if __name__ == "__main__":
    main()
