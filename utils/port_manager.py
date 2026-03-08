from __future__ import annotations

import argparse
import json
import os
import re
import socket
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import find_dotenv, load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"
RUNTIME_DIR = PROJECT_ROOT / ".runtime"
RUNTIME_STATE_PATH = RUNTIME_DIR / "service_ports.json"
GLOBAL_REGISTRY_PATH = Path.home() / ".local_ports_registry.json"
DEFAULT_RANGE_START = 21000
DEFAULT_RANGE_END = 21050


@dataclass(frozen=True)
class ServiceDefinition:
    key: str
    label: str
    env_var: str
    default_port: int
    bind_host_env: str
    public_host_env: str
    default_bind_host: str = "0.0.0.0"
    default_public_host: str = "127.0.0.1"
    scheme: str = "http"


SERVICE_DEFINITIONS: dict[str, ServiceDefinition] = {
    "dashboard_api": ServiceDefinition(
        key="dashboard_api",
        label="Dashboard API",
        env_var="API_PORT",
        default_port=21010,
        bind_host_env="API_BIND_HOST",
        public_host_env="API_PUBLIC_HOST",
        default_bind_host="0.0.0.0",
        default_public_host="127.0.0.1",
    ),
    "dashboard_frontend": ServiceDefinition(
        key="dashboard_frontend",
        label="Dashboard Frontend",
        env_var="FRONTEND_PORT",
        default_port=21011,
        bind_host_env="FRONTEND_BIND_HOST",
        public_host_env="FRONTEND_PUBLIC_HOST",
        default_bind_host="0.0.0.0",
        default_public_host="127.0.0.1",
    ),
    "automation_ui": ServiceDefinition(
        key="automation_ui",
        label="Automation Service",
        env_var="AUTOMATION_PORT",
        default_port=21012,
        bind_host_env="AUTOMATION_BIND_HOST",
        public_host_env="AUTOMATION_PUBLIC_HOST",
        default_bind_host="127.0.0.1",
        default_public_host="127.0.0.1",
    ),
    "metrics": ServiceDefinition(
        key="metrics",
        label="Metrics Service",
        env_var="METRICS_PORT",
        default_port=21013,
        bind_host_env="METRICS_BIND_HOST",
        public_host_env="METRICS_PUBLIC_HOST",
        default_bind_host="127.0.0.1",
        default_public_host="127.0.0.1",
    ),
}


def load_environment() -> None:
    dotenv_path = find_dotenv(usecwd=True)
    load_dotenv(dotenv_path or ENV_PATH, override=False)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "project"


def get_project_slug() -> str:
    load_environment()
    explicit = os.getenv("PROJECT_SLUG") or os.getenv("PROJECT_NAME")
    return _slugify(explicit or PROJECT_ROOT.name)


def get_project_name() -> str:
    load_environment()
    return os.getenv("PROJECT_NAME") or PROJECT_ROOT.name


def get_port_range() -> tuple[int, int]:
    load_environment()
    start = int(os.getenv("PORT_RANGE_START", DEFAULT_RANGE_START))
    end = int(os.getenv("PORT_RANGE_END", DEFAULT_RANGE_END))
    if start > end:
        start, end = end, start
    return start, end


def _read_json_file(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_runtime_state() -> dict[str, Any]:
    default = {
        "project": {
            "name": get_project_name(),
            "slug": get_project_slug(),
            "path": str(PROJECT_ROOT),
            "range": {"start": get_port_range()[0], "end": get_port_range()[1]},
        },
        "services": {},
    }
    return _read_json_file(RUNTIME_STATE_PATH, default)


def write_runtime_state(state: dict[str, Any]) -> None:
    _write_json_file(RUNTIME_STATE_PATH, state)


def register_project_range() -> None:
    start, end = get_port_range()
    registry = _read_json_file(GLOBAL_REGISTRY_PATH, {})
    registry[get_project_slug()] = {
        "project_name": get_project_name(),
        "range": f"{start}-{end}",
        "path": str(PROJECT_ROOT),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_json_file(GLOBAL_REGISTRY_PATH, registry)


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind((host, port))
        except OSError:
            return False
    return True


def _port_in_range(port: int) -> bool:
    start, end = get_port_range()
    return start <= port <= end


def _parse_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _find_free_port(preferred_port: int | None, occupied: set[int]) -> int:
    start, end = get_port_range()
    candidate_order: list[int] = []
    if preferred_port is not None and start <= preferred_port <= end:
        candidate_order.append(preferred_port)
    candidate_order.extend(port for port in range(start, end + 1) if port != preferred_port)

    for candidate in candidate_order:
        if candidate in occupied:
            continue
        if is_port_available(candidate):
            return candidate
    raise RuntimeError(f"No free ports available in dedicated range {start}-{end}")


def _service_hosts(definition: ServiceDefinition) -> tuple[str, str]:
    bind_host = os.getenv(definition.bind_host_env, definition.default_bind_host)
    public_host = os.getenv(definition.public_host_env, definition.default_public_host)
    return bind_host, public_host


def ensure_service_assignment(service_key: str) -> dict[str, Any]:
    load_environment()
    register_project_range()

    if service_key not in SERVICE_DEFINITIONS:
        raise KeyError(f"Unknown service key: {service_key}")

    definition = SERVICE_DEFINITIONS[service_key]
    state = read_runtime_state()
    services = state.setdefault("services", {})
    existing = services.get(service_key, {})
    occupied = {
        int(service_state["port"])
        for key, service_state in services.items()
        if key != service_key and _parse_int(service_state.get("port")) is not None
    }

    requested_port = _parse_int(os.getenv(definition.env_var))
    runtime_port = _parse_int(existing.get("port"))
    preferred_port = requested_port if requested_port is not None else runtime_port or definition.default_port
    messages: list[str] = []

    if preferred_port is not None and not _port_in_range(preferred_port):
        start, end = get_port_range()
        messages.append(
            f"{definition.env_var}={preferred_port} is outside dedicated range {start}-{end}; selecting a valid local port instead"
        )
        preferred_port = definition.default_port

    assigned_port = preferred_port
    if assigned_port in occupied:
        messages.append(f"Port {assigned_port} is already assigned to another TraderFund local service")
        assigned_port = None

    if assigned_port is not None and not is_port_available(assigned_port):
        messages.append(f"Port {assigned_port} is already in use")
        assigned_port = None

    if assigned_port is None:
        assigned_port = _find_free_port(preferred_port, occupied)
        messages.append(f"Switching {definition.env_var} to {assigned_port}")

    bind_host, public_host = _service_hosts(definition)
    assignment = {
        "service": service_key,
        "label": definition.label,
        "env_var": definition.env_var,
        "port": assigned_port,
        "bind_host": bind_host,
        "public_host": public_host,
        "url": f"{definition.scheme}://{public_host}:{assigned_port}",
        "messages": messages,
        "assigned_at": datetime.now(timezone.utc).isoformat(),
    }

    os.environ[definition.env_var] = str(assigned_port)
    services[service_key] = assignment
    state["project"] = {
        "name": get_project_name(),
        "slug": get_project_slug(),
        "path": str(PROJECT_ROOT),
        "range": {"start": get_port_range()[0], "end": get_port_range()[1]},
        "registry_path": str(GLOBAL_REGISTRY_PATH),
    }
    write_runtime_state(state)
    return assignment


def ensure_service_assignments(service_keys: list[str]) -> dict[str, dict[str, Any]]:
    return {service_key: ensure_service_assignment(service_key) for service_key in service_keys}


def _read_service_assignment(service_key: str) -> dict[str, Any] | None:
    state = read_runtime_state()
    return state.get("services", {}).get(service_key)


def get_service_port(service_key: str) -> int:
    load_environment()
    definition = SERVICE_DEFINITIONS[service_key]
    runtime_assignment = _read_service_assignment(service_key) or {}
    return _parse_int(runtime_assignment.get("port")) or _parse_int(os.getenv(definition.env_var)) or definition.default_port


def get_service_url(service_key: str, path_suffix: str = "") -> str:
    load_environment()
    definition = SERVICE_DEFINITIONS[service_key]
    runtime_assignment = _read_service_assignment(service_key) or {}
    public_host = runtime_assignment.get("public_host") or os.getenv(definition.public_host_env, definition.default_public_host)
    port = get_service_port(service_key)
    base = f"{definition.scheme}://{public_host}:{port}"
    if not path_suffix:
        return base
    if path_suffix.startswith("/"):
        return f"{base}{path_suffix}"
    return f"{base}/{path_suffix}"


def get_api_base_url(include_api_prefix: bool = True) -> str:
    return get_service_url("dashboard_api", "/api" if include_api_prefix else "")


def render_service_map(assignments: dict[str, dict[str, Any]] | None = None) -> str:
    assignments = assignments or read_runtime_state().get("services", {})
    lines = [
        get_project_name(),
        f"Dedicated Range: {get_port_range()[0]}-{get_port_range()[1]}",
    ]
    for service_key, definition in SERVICE_DEFINITIONS.items():
        assignment = assignments.get(service_key)
        if not assignment:
            lines.append(f"{definition.label}: unassigned")
            continue
        lines.append(f"{definition.label}: {assignment['url']}")
    return "\n".join(lines)


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TraderFund local port manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    assign_parser = subparsers.add_parser("assign", help="Assign one or more service ports within the dedicated project range")
    assign_parser.add_argument("services", nargs="+", choices=sorted(SERVICE_DEFINITIONS.keys()))
    assign_parser.add_argument("--json", action="store_true", help="Print assignments as JSON")

    show_parser = subparsers.add_parser("show", help="Show current local service map")
    show_parser.add_argument("--json", action="store_true", help="Print service map as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_cli()
    args = parser.parse_args(argv)

    if args.command == "assign":
        assignments = ensure_service_assignments(args.services)
        if args.json:
            print(json.dumps(assignments, indent=2))
        else:
            for assignment in assignments.values():
                for message in assignment.get("messages", []):
                    print(message)
            print(render_service_map())
        return 0

    if args.command == "show":
        state = read_runtime_state()
        if args.json:
            print(json.dumps(state, indent=2))
        else:
            print(render_service_map(state.get("services", {})))
        return 0

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())