import json
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
TRUTH_EPOCH_PATH = PROJECT_ROOT / "docs" / "epistemic" / "truth_epoch.json"


def load_truth_epoch_id() -> str:
    if not TRUTH_EPOCH_PATH.exists():
        return "UNKNOWN"
    try:
        with open(TRUTH_EPOCH_PATH, "r", encoding="utf-8") as file_handle:
            payload = json.load(file_handle)
        return payload.get("epoch", {}).get("epoch_id", "UNKNOWN")
    except Exception:
        return "UNKNOWN"


def attach_provenance(payload: Dict[str, Any], source_artifact: str, truth_epoch: str | None = None) -> Dict[str, Any]:
    epoch_id = truth_epoch or load_truth_epoch_id() or payload.get("truth_epoch") or "UNKNOWN"
    payload["source_artifact"] = source_artifact
    payload["trace_id"] = f"{source_artifact}::{epoch_id}"
    payload["epoch_bounded"] = epoch_id != "UNKNOWN"
    payload.setdefault("truth_epoch", epoch_id)
    trace = payload.setdefault("trace", {})
    trace.setdefault("source", source_artifact)
    trace.setdefault("trace_id", payload["trace_id"])
    trace.setdefault("epoch_bounded", payload["epoch_bounded"])
    return payload
