from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.port_manager import ensure_service_assignments, render_service_map


def main() -> int:
    assignments = ensure_service_assignments(["dashboard_api", "dashboard_frontend"])
    for assignment in assignments.values():
        for message in assignment.get("messages", []):
            print(message)
    print(render_service_map())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())