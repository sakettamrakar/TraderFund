"""
Canonical Artifact Contract (RR-B.3)

Declares every artifact the pipeline can produce: its canonical path pattern,
producer stage, schema version, and required columns/fields.

The manifest is the single source of truth that validators, dashboard loaders,
and pipeline stages use to locate data.  No component should hard-code artifact
paths — they should resolve through the manifest or through this contract.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Artifact Descriptor ──────────────────────────────────────────────────────

@dataclass
class ArtifactDescriptor:
    """Describes one canonical artifact in the pipeline."""
    artifact_id: str
    producer: str               # which pipeline stage creates this
    description: str
    path_pattern: str           # glob-style, relative to repo root
    schema_version: str = "1.0"
    required_columns: List[str] = field(default_factory=list)
    format: str = ""            # jsonl, parquet, json, csv, etc.
    market_scoped: bool = True  # does path change per market mode?
    notes: str = ""


# ── Contract Registry ────────────────────────────────────────────────────────

ARTIFACT_CONTRACT: Dict[str, ArtifactDescriptor] = {}


def _register(desc: ArtifactDescriptor) -> ArtifactDescriptor:
    ARTIFACT_CONTRACT[desc.artifact_id] = desc
    return desc


# ── Ingestion artifacts ──────────────────────────────────────────────────────

_register(ArtifactDescriptor(
    artifact_id="ingestion_raw_india",
    producer="ingestion.angel_smartapi",
    description="Raw intraday OHLC ticks from Angel One SmartAPI",
    path_pattern="data/raw/api_based/angel/intraday_ohlc/*.jsonl",
    format="jsonl",
    required_columns=["symbol", "exchange", "interval", "timestamp",
                      "open", "high", "low", "close", "volume",
                      "source", "ingestion_ts"],
    schema_version="1.0",
))

_register(ArtifactDescriptor(
    artifact_id="ingestion_raw_us",
    producer="ingestion.alpha_vantage",
    description="US daily OHLCV data from Alpha Vantage",
    path_pattern="data/raw/us/*/*_daily.json",
    format="json",
    required_columns=["timestamp", "open", "high", "low", "close", "volume"],
    schema_version="1.0",
))

_register(ArtifactDescriptor(
    artifact_id="ingestion_processed_india",
    producer="processing.intraday_candles_processor",
    description="Cleaned, deduplicated intraday candles (Parquet)",
    path_pattern="data/processed/candles/intraday/*.parquet",
    format="parquet",
    required_columns=["symbol", "exchange", "timestamp",
                      "open", "high", "low", "close", "volume"],
    schema_version="1.0",
))

# ── Fixture artifacts ────────────────────────────────────────────────────────

_register(ArtifactDescriptor(
    artifact_id="fixture_raw",
    producer="fixture_generator",
    description="Fixture raw data for testing",
    path_pattern="data/fixtures/raw/*.jsonl",
    format="jsonl",
    required_columns=["symbol", "exchange", "interval", "timestamp",
                      "open", "high", "low", "close", "volume",
                      "source", "ingestion_ts"],
    schema_version="1.0",
    market_scoped=False,
))

_register(ArtifactDescriptor(
    artifact_id="fixture_processed",
    producer="fixture_generator",
    description="Fixture processed candles for testing",
    path_pattern="data/fixtures/processed/*.parquet",
    format="parquet",
    required_columns=["symbol", "exchange", "timestamp",
                      "open", "high", "low", "close", "volume"],
    schema_version="1.0",
    market_scoped=False,
))

_register(ArtifactDescriptor(
    artifact_id="fixture_us_daily",
    producer="fixture_generator",
    description="Fixture US daily JSON for testing",
    path_pattern="data/fixtures/us/*.json",
    format="json",
    required_columns=["timestamp", "open", "high", "low", "close", "volume"],
    schema_version="1.0",
    market_scoped=False,
))

# ── Research artifacts ───────────────────────────────────────────────────────

_register(ArtifactDescriptor(
    artifact_id="research_intelligence_snapshot",
    producer="intelligence.engine",
    description="Intelligence attention signals snapshot",
    path_pattern="docs/intelligence/intelligence_*_{date}.json",
    format="json",
    required_columns=[],
    schema_version="1.0",
))

_register(ArtifactDescriptor(
    artifact_id="research_factor_context",
    producer="evolution.factor_context_builder",
    description="Factor context for evaluation window",
    path_pattern="docs/evolution/context/*.json",
    format="json",
    required_columns=[],
    schema_version="1.0",
))

# ── Evaluation artifacts ─────────────────────────────────────────────────────

_register(ArtifactDescriptor(
    artifact_id="evaluation_activation_matrix",
    producer="evolution.pipeline_runner",
    description="Strategy activation matrix CSV",
    path_pattern="docs/evolution/evaluation/**/strategy_activation_matrix.csv",
    format="csv",
    required_columns=["strategy_id", "decisions", "shadow", "failures", "regime"],
    schema_version="1.0",
))

_register(ArtifactDescriptor(
    artifact_id="evaluation_decision_trace",
    producer="evolution.pipeline_runner",
    description="Decision trace log",
    path_pattern="docs/evolution/evaluation/**/decision_trace_log.parquet",
    format="parquet",
    required_columns=[],
    schema_version="1.0",
))

# ── Dashboard artifacts ──────────────────────────────────────────────────────

_register(ArtifactDescriptor(
    artifact_id="dashboard_system_status",
    producer="dashboard.loaders.system_status",
    description="System status payload for dashboard",
    path_pattern="logs/validation/*_latest.json",
    format="json",
    required_columns=[],
    schema_version="1.0",
    market_scoped=False,
))

# ── Pipeline manifest ────────────────────────────────────────────────────────

_register(ArtifactDescriptor(
    artifact_id="pipeline_manifest",
    producer="traderfund.pipeline.daily",
    description="Artifact manifest emitted by the canonical daily pipeline",
    path_pattern="logs/validation/pipeline_manifest.json",
    format="json",
    required_columns=[],
    schema_version="1.0",
    market_scoped=False,
))


# ── Manifest dataclass ───────────────────────────────────────────────────────

@dataclass
class ManifestEntry:
    """One artifact entry inside the pipeline manifest."""
    artifact_id: str
    producer: str
    path: str                   # resolved absolute or relative path
    schema_version: str
    format: str
    produced_at: str            # ISO-8601
    market_mode: str
    status: str = "present"     # present | missing | skipped
    missing_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineManifest:
    """
    The pipeline manifest is the single output of a daily pipeline run.
    Every downstream consumer (validation, dashboard) reads this to find
    artifact locations and freshness.
    """
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    market_mode: str = "fixture"
    pipeline_version: str = "1.0"
    entries: List[ManifestEntry] = field(default_factory=list)
    validation_summaries: Dict[str, Any] = field(default_factory=dict)

    def add_entry(self, entry: ManifestEntry) -> None:
        self.entries.append(entry)

    def get_entry(self, artifact_id: str) -> Optional[ManifestEntry]:
        for entry in self.entries:
            if entry.artifact_id == artifact_id:
                return entry
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "market_mode": self.market_mode,
            "pipeline_version": self.pipeline_version,
            "entries": [e.to_dict() for e in self.entries],
            "validation_summaries": self.validation_summaries,
        }

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def read(cls, path: Path) -> "PipelineManifest":
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = [ManifestEntry(**e) for e in data.get("entries", [])]
        return cls(
            generated_at=data["generated_at"],
            market_mode=data["market_mode"],
            pipeline_version=data.get("pipeline_version", "1.0"),
            entries=entries,
            validation_summaries=data.get("validation_summaries", {}),
        )


def build_manifest_for_mode(
    market_mode: str,
    repo_root: Path,
) -> PipelineManifest:
    """
    Build a manifest by scanning which declared artifacts exist on disk
    for the given market mode.
    """
    from .market_modes import get_mode_spec

    spec = get_mode_spec(market_mode)
    manifest = PipelineManifest(market_mode=market_mode)
    now = datetime.now(timezone.utc).isoformat()

    for artifact_id, descriptor in ARTIFACT_CONTRACT.items():
        # Determine the pattern to search
        pattern = descriptor.path_pattern

        # For fixture mode, only include fixture artifacts
        if spec.is_fixture and not artifact_id.startswith("fixture_") and artifact_id != "pipeline_manifest":
            continue

        # For live modes, skip fixture-only artifacts
        if not spec.is_fixture and artifact_id.startswith("fixture_"):
            continue

        # Resolve on disk
        matches = sorted(repo_root.glob(pattern))
        if matches:
            resolved_path = str(matches[-1].relative_to(repo_root))
            status = "present"
            missing_reason = ""
        else:
            resolved_path = pattern
            status = "missing"
            missing_reason = f"No files matching '{pattern}' found in repo root"

        manifest.add_entry(ManifestEntry(
            artifact_id=artifact_id,
            producer=descriptor.producer,
            path=resolved_path,
            schema_version=descriptor.schema_version,
            format=descriptor.format,
            produced_at=now if status == "present" else "",
            market_mode=market_mode,
            status=status,
            missing_reason=missing_reason,
        ))

    return manifest
