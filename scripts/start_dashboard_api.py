from __future__ import annotations

import argparse
import sys
from pathlib import Path

import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.port_manager import ensure_service_assignment, render_service_map


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Start the TraderFund dashboard API with managed local ports")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload mode")
    args = parser.parse_args(argv)

    assignment = ensure_service_assignment("dashboard_api")
    for message in assignment.get("messages", []):
        print(message)
    print(render_service_map())

    uvicorn.run(
        "dashboard.backend.app:app",
        app_dir="src",
        host=assignment["bind_host"],
        port=int(assignment["port"]),
        reload=args.reload,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())