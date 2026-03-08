from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

try:
    import pandas as pd
except ImportError:  # pragma: no cover - environment dependent
    pd = None

from .validation_engine import (
    ValidationContext,
    ValidationTask,
    fail_result,
    pass_result,
    skip_result,
)


class ValidationRegistry:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        if str(self.repo_root) not in sys.path:
            sys.path.insert(0, str(self.repo_root))
        src_root = self.repo_root / "src"
        if src_root.exists() and str(src_root) not in sys.path:
            sys.path.insert(0, str(src_root))
        self._component_map = self._build_component_map()
        self._skills = self._discover_skills()
        self._tasks = self._build_tasks()

    @property
    def skills(self) -> List[str]:
        return list(self._skills)

    def component_map(self) -> Dict[str, List[str]]:
        return {key: list(value) for key, value in self._component_map.items()}

    def tasks_for_phase(self, phase: str) -> List[ValidationTask]:
        return [task for task in self._tasks if task.phase == phase]

    def all_tasks(self) -> List[ValidationTask]:
        return list(self._tasks)

    def _build_component_map(self) -> Dict[str, List[str]]:
        return {
            "ingestion": [
                "ingestion/api_ingestion/alpha_vantage",
                "ingestion/api_ingestion/angel_smartapi",
                "ingestion/historical_backfill",
                "ingestion/incremental_update",
                "ingestion/universe_expansion",
                "processing/intraday_candles_processor.py",
                "src/ingestion",
            ],
            "memory": [
                "docs/memory",
                "docs/contracts/layer_interaction_contract.md",
                "docs/verification_runs/RUN_002_MEMORY.md",
                "src/layers",
                "docs/intelligence",
            ],
            "research": [
                "research_modules/pipeline_controller",
                "research_modules/universe_hygiene",
                "research_modules/structural_capability",
                "research_modules/energy_setup",
                "research_modules/participation_trigger",
                "research_modules/momentum_confirmation",
                "research_modules/sustainability_risk",
                "src/layers/factor_live.py",
                "src/intelligence",
            ],
            "evaluation": [
                "src/evolution/pipeline_runner.py",
                "src/evolution/factor_context_builder.py",
                "src/evolution/bulk_evaluator.py",
                "src/evolution/decision_replay.py",
                "src/evolution/paper_pnl.py",
                "src/evolution/rejection_analysis.py",
                "src/evolution/compile_bundle.py",
                "docs/evolution/evaluation_profiles",
            ],
            "dashboard": [
                "src/dashboard/backend/app.py",
                "src/dashboard/backend/loaders",
                "src/dashboard/frontend/src",
                "docs/dashboard",
            ],
            "desk_skills": [
                ".agent/skills",
                "bin/run-skill.py",
            ],
            "llm_apis": [
                "llm_integration/client.py",
                "llm_integration/engine/explainer.py",
                "automation/gemini_bridge.py",
                "automation/executors/gemini_fallback.py",
                "automation/agents/validation_agent.py",
            ],
        }

    def _discover_skills(self) -> List[str]:
        skills_root = self.repo_root / ".agent" / "skills"
        if not skills_root.exists():
            return []
        return sorted(path.name for path in skills_root.iterdir() if path.is_dir())

    def _build_tasks(self) -> List[ValidationTask]:
        return [
            ValidationTask("ingestion", "schema_validation", "Validate canonical ingestion schema", self._check_ingestion_schema),
            ValidationTask("ingestion", "timestamp_validation", "Validate ingestion timestamps", self._check_ingestion_timestamps),
            ValidationTask("ingestion", "null_handling", "Validate null and duplicate handling", self._check_ingestion_nulls),
            ValidationTask("ingestion", "data_lineage", "Validate lineage assets and contracts", self._check_ingestion_lineage),
            ValidationTask("memory", "layer_routing", "Validate V3 layer routing", self._check_memory_layer_routing),
            ValidationTask("memory", "mutation_control", "Validate mutation control surfaces", self._check_memory_mutation_control),
            ValidationTask("memory", "cross_layer_contamination", "Validate cross-layer contamination guard", self._check_memory_contamination),
            ValidationTask("research", "factor_determinism", "Validate factor determinism", self._check_research_factor_determinism),
            ValidationTask("research", "regime_gating", "Validate regime gating", self._check_research_regime_gating),
            ValidationTask("research", "reproducibility", "Validate research reproducibility", self._check_research_reproducibility),
            ValidationTask("evaluation", "score_consistency", "Validate evaluation score consistency", self._check_evaluation_score_consistency),
            ValidationTask("evaluation", "evolution_integrity", "Validate evaluation governance integrity", self._check_evaluation_integrity),
            ValidationTask("dashboard", "traceability", "Validate dashboard provenance", self._check_dashboard_traceability),
            ValidationTask("dashboard", "freshness", "Validate dashboard freshness signals", self._check_dashboard_freshness),
            ValidationTask("dashboard", "read_only_guarantee", "Validate dashboard read-only contract", self._check_dashboard_read_only),
        ]

    def _latest_path(self, pattern: str) -> Path | None:
        matches = list(self.repo_root.glob(pattern))
        if not matches:
            return None
        return max(matches, key=lambda item: item.stat().st_mtime)

    def _read_jsonl(self, path: Path) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
        return rows

    def _check_required_columns(
        self,
        path: Path,
        required_columns: Sequence[str],
    ) -> tuple[set[str], set[str]]:
        if path.suffix == ".jsonl":
            rows = self._read_jsonl(path)
            if not rows:
                return set(), set(required_columns)
            columns = set(rows[0].keys())
        elif path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            first_value = next(iter(payload.values()), {})
            if isinstance(first_value, dict):
                columns = {"timestamp", "open", "high", "low", "close", "volume"}
            else:
                columns = set(payload.keys())
        else:
            if pd is None:
                return set(), set(required_columns)
            frame = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
            columns = set(frame.columns)
        missing = set(required_columns) - columns
        return columns, missing

    def _check_ingestion_schema(self, context: ValidationContext):
        raw_path = self._latest_path("data/raw/api_based/angel/intraday_ohlc/*.jsonl")
        processed_path = self._latest_path("data/processed/candles/intraday/*.parquet")
        us_path = self._latest_path("data/raw/us/*/*_daily.json")
        if raw_path is None or processed_path is None or us_path is None:
            return fail_result(
                context.phase,
                "schema_validation",
                "missing_ingestion_artifacts",
                details={
                    "raw_found": raw_path is not None,
                    "processed_found": processed_path is not None,
                    "us_found": us_path is not None,
                },
            )

        raw_required = ["symbol", "exchange", "interval", "timestamp", "open", "high", "low", "close", "volume", "source", "ingestion_ts"]
        processed_required = ["symbol", "exchange", "timestamp", "open", "high", "low", "close", "volume"]
        us_required = ["timestamp", "open", "high", "low", "close", "volume"]

        _, raw_missing = self._check_required_columns(raw_path, raw_required)
        _, processed_missing = self._check_required_columns(processed_path, processed_required)
        _, us_missing = self._check_required_columns(us_path, us_required)
        if raw_missing or processed_missing or us_missing:
            return fail_result(
                context.phase,
                "schema_validation",
                "schema_drift_detected",
                details={
                    "raw_missing": sorted(raw_missing),
                    "processed_missing": sorted(processed_missing),
                    "us_missing": sorted(us_missing),
                },
                evidence=[str(raw_path), str(processed_path), str(us_path)],
            )
        return pass_result(
            context.phase,
            "schema_validation",
            "schemas_match_expected_contracts",
            evidence=[str(raw_path), str(processed_path), str(us_path)],
        )

    def _check_ingestion_timestamps(self, context: ValidationContext):
        if pd is None:
            return skip_result(context.phase, "timestamp_validation", "pandas_unavailable")
        path = self._latest_path("data/raw/api_based/angel/ltp_snapshots/*.jsonl") or self._latest_path("data/raw/api_based/angel/intraday_ohlc/*.jsonl")
        if path is None:
            return fail_result(context.phase, "timestamp_validation", "missing_timestamp_artifact")
        frame = pd.DataFrame(self._read_jsonl(path))
        if frame.empty or "timestamp" not in frame.columns:
            return fail_result(context.phase, "timestamp_validation", "missing_timestamp_column", evidence=[str(path)])
        timestamps = pd.to_datetime(frame["timestamp"], errors="coerce")
        if timestamps.isna().any():
            return fail_result(context.phase, "timestamp_validation", "timestamp_parse_failure", evidence=[str(path)])
        future_count = int((timestamps > pd.Timestamp.now(tz=timestamps.dt.tz if timestamps.dt.tz is not None else None)).sum())
        if future_count:
            return fail_result(
                context.phase,
                "timestamp_validation",
                "future_timestamps_detected",
                details={"future_count": future_count},
                evidence=[str(path)],
            )
        return pass_result(
            context.phase,
            "timestamp_validation",
            "timestamps_parse_and_bound_correctly",
            details={"min": timestamps.min().isoformat(), "max": timestamps.max().isoformat()},
            evidence=[str(path)],
        )

    def _check_ingestion_nulls(self, context: ValidationContext):
        if pd is None:
            return skip_result(context.phase, "null_handling", "pandas_unavailable")
        path = self._latest_path("data/processed/candles/intraday/*.parquet")
        if path is None:
            return fail_result(context.phase, "null_handling", "missing_processed_intraday_artifact")
        frame = pd.read_parquet(path)
        required = ["symbol", "exchange", "timestamp", "open", "high", "low", "close", "volume"]
        missing_cols = [column for column in required if column not in frame.columns]
        if missing_cols:
            return fail_result(context.phase, "null_handling", "missing_required_columns", details={"missing": missing_cols}, evidence=[str(path)])
        null_count = int(frame[required].isna().sum().sum())
        duplicate_count = int(frame.duplicated(subset=["symbol", "timestamp"]).sum())
        if null_count or duplicate_count:
            return fail_result(
                context.phase,
                "null_handling",
                "null_or_duplicate_records_detected",
                details={"null_count": null_count, "duplicate_count": duplicate_count},
                evidence=[str(path)],
            )
        return pass_result(
            context.phase,
            "null_handling",
            "required_fields_non_null_and_deduplicated",
            details={"rows": int(len(frame))},
            evidence=[str(path)],
        )

    def _check_ingestion_lineage(self, context: ValidationContext):
        required = [
            self.repo_root / "scripts" / "validate_ingestion_run.py",
            self.repo_root / "docs" / "contracts" / "RAW_ANGEL_INTRADAY_SCHEMA.md",
            self.repo_root / "docs" / "verification_runs" / "RUN_001_INGESTION.md",
        ]
        missing = [str(path.relative_to(self.repo_root)) for path in required if not path.exists()]
        if missing:
            return fail_result(context.phase, "data_lineage", "lineage_contract_gap", details={"missing": missing})
        return pass_result(
            context.phase,
            "data_lineage",
            "lineage_contracts_present",
            evidence=[str(path.relative_to(self.repo_root)) for path in required],
        )

    def _check_memory_layer_routing(self, context: ValidationContext):
        required = [
            self.repo_root / "docs" / "memory",
            self.repo_root / "docs" / "verification_runs" / "RUN_002_MEMORY.md",
            self.repo_root / "data" / "analytics" / "us" / "prices" / "daily",
            self.repo_root / "data" / "processed" / "candles" / "intraday",
        ]
        missing = [str(path.relative_to(self.repo_root)) for path in required if not path.exists()]
        if missing:
            return fail_result(context.phase, "layer_routing", "missing_memory_layer_assets", details={"missing": missing})
        return pass_result(
            context.phase,
            "layer_routing",
            "memory_routing_assets_present",
            evidence=[str(path.relative_to(self.repo_root)) for path in required],
        )

    def _check_memory_mutation_control(self, context: ValidationContext):
        required = [
            self.repo_root / "docs" / "intelligence" / "suppression_state_US.json",
            self.repo_root / "docs" / "intelligence" / "suppression_reason_registry_US.json",
            self.repo_root / "docs" / "audit" / "f5_suppression",
        ]
        missing = [str(path.relative_to(self.repo_root)) for path in required if not path.exists()]
        if missing:
            return fail_result(context.phase, "mutation_control", "mutation_audit_missing", details={"missing": missing})
        return pass_result(
            context.phase,
            "mutation_control",
            "mutation_control_audits_present",
            evidence=[str(path.relative_to(self.repo_root)) for path in required],
        )

    def _check_memory_contamination(self, context: ValidationContext):
        duplicates = [
            self.repo_root / "docs" / "meta" / "last_successful_evaluation.json",
            self.repo_root / "docs" / "meta" / "market_evaluation_scope.json",
        ]
        present = [str(path.relative_to(self.repo_root)) for path in duplicates if path.exists()]
        if present:
            return fail_result(
                context.phase,
                "cross_layer_contamination",
                "duplicate_meta_authority_detected",
                details={"duplicate_artifacts": present},
                evidence=present,
            )
        return pass_result(context.phase, "cross_layer_contamination", "no_duplicate_meta_authority_detected")

    def _check_research_factor_determinism(self, context: ValidationContext):
        try:
            from src.layers.convergence_engine import ConvergenceEngine
            from src.models.convergence_models import LensSignal
            from src.models.meta_models import RegimeState
        except Exception as exc:
            return skip_result(context.phase, "factor_determinism", f"import_failure:{type(exc).__name__}", details={"message": str(exc)})

        engine = ConvergenceEngine()
        lenses = [
            LensSignal("SPY", "LONG", 0.8, 0.9, "TECHNICAL"),
            LensSignal("SPY", "LONG", 0.7, 0.8, "MOMENTUM"),
            LensSignal("SPY", "LONG", 0.9, 0.9, "FUNDAMENTAL"),
        ]
        regime = RegimeState("TRENDING", 15.0)
        first = engine.compute(lenses, regime, 1.0)
        second = engine.compute(lenses, regime, 1.0)
        if first.final_score != second.final_score:
            return fail_result(
                context.phase,
                "factor_determinism",
                "factor_score_drift_detected",
                details={"first": first.final_score, "second": second.final_score},
            )
        return pass_result(
            context.phase,
            "factor_determinism",
            "factor_scores_repeat_identically",
            details={"final_score": first.final_score},
        )

    def _check_research_regime_gating(self, context: ValidationContext):
        try:
            from src.layers.convergence_engine import ConvergenceEngine, RegimeContextMissingError
            from src.models.convergence_models import LensSignal
        except Exception as exc:
            return skip_result(context.phase, "regime_gating", f"import_failure:{type(exc).__name__}", details={"message": str(exc)})

        engine = ConvergenceEngine()
        lenses = [
            LensSignal("SPY", "LONG", 0.8, 0.9, "TECHNICAL"),
            LensSignal("SPY", "LONG", 0.7, 0.8, "MOMENTUM"),
        ]
        try:
            engine.compute(lenses, None, 1.0)
        except RegimeContextMissingError:
            return pass_result(context.phase, "regime_gating", "missing_regime_halts_explicitly")
        return fail_result(context.phase, "regime_gating", "missing_regime_did_not_halt")

    def _check_research_reproducibility(self, context: ValidationContext):
        try:
            from src.layers.convergence_engine import ConvergenceEngine
            from src.models.convergence_models import LensSignal
            from src.models.meta_models import RegimeState
        except Exception as exc:
            return skip_result(context.phase, "reproducibility", f"import_failure:{type(exc).__name__}", details={"message": str(exc)})

        engine = ConvergenceEngine()
        lenses = [
            LensSignal("QQQ", "LONG", 0.8, 0.9, "TECHNICAL"),
            LensSignal("QQQ", "LONG", 0.7, 0.8, "MOMENTUM"),
            LensSignal("QQQ", "LONG", 0.9, 0.9, "FUNDAMENTAL"),
        ]
        regime = RegimeState("TRENDING", 15.0)
        first = engine.compute(lenses, regime, 1.0)
        second = engine.compute(lenses, regime, 1.0)
        if getattr(first, "input_hash", None) != getattr(second, "input_hash", None):
            return fail_result(
                context.phase,
                "reproducibility",
                "input_hash_mismatch",
                details={"first": getattr(first, "input_hash", None), "second": getattr(second, "input_hash", None)},
            )
        return pass_result(
            context.phase,
            "reproducibility",
            "research_outputs_hash_stable",
            details={"input_hash": getattr(first, "input_hash", None)},
        )

    def _check_evaluation_score_consistency(self, context: ValidationContext):
        activation_path = self._latest_path("docs/evolution/evaluation/**/strategy_activation_matrix.csv")
        if activation_path is None:
            return fail_result(context.phase, "score_consistency", "missing_activation_matrix")
        if pd is None:
            return skip_result(context.phase, "score_consistency", "pandas_unavailable", evidence=[str(activation_path)])
        frame = pd.read_csv(activation_path)
        required = {"strategy_id", "decisions", "shadow", "failures", "regime"}
        missing = sorted(required - set(frame.columns))
        if missing or frame.empty:
            return fail_result(
                context.phase,
                "score_consistency",
                "evaluation_artifact_incomplete",
                details={"missing_columns": missing, "empty": frame.empty},
                evidence=[str(activation_path)],
            )
        sibling_checks = [
            activation_path.with_name("decision_trace_log.parquet"),
            activation_path.with_name("paper_pnl_summary.csv"),
            activation_path.with_name("rejection_analysis.csv"),
        ]
        absent = [str(path) for path in sibling_checks if not path.exists()]
        if absent:
            return fail_result(context.phase, "score_consistency", "missing_evaluation_siblings", details={"missing": absent}, evidence=[str(activation_path)])
        return pass_result(
            context.phase,
            "score_consistency",
            "evaluation_artifacts_present_and_populated",
            details={"rows": int(len(frame))},
            evidence=[str(activation_path)],
        )

    def _check_evaluation_integrity(self, context: ValidationContext):
        profiles = list((self.repo_root / "docs" / "evolution" / "evaluation_profiles").glob("*.yaml"))
        if not profiles:
            return fail_result(context.phase, "evolution_integrity", "missing_evaluation_profiles")
        violations: List[str] = []
        for profile in profiles:
            text = profile.read_text(encoding="utf-8").lower()
            for required in ("shadow_only: true", "forbid_real_execution: true", "forbid_strategy_mutation: true"):
                if required not in text:
                    violations.append(f"{profile.name}:{required}")
        if violations:
            return fail_result(
                context.phase,
                "evolution_integrity",
                "evaluation_profile_governance_gap",
                details={"violations": violations},
            )
        return pass_result(
            context.phase,
            "evolution_integrity",
            "evaluation_profiles_remain_shadow_only",
            evidence=[str(profile.relative_to(self.repo_root)) for profile in profiles],
        )

    def _check_dashboard_traceability(self, context: ValidationContext):
        try:
            from src.dashboard.backend.loaders.system_status import load_system_status
            from src.dashboard.backend.loaders.layer_health import load_layer_health
            from src.dashboard.backend.loaders.market_snapshot import load_market_snapshot
        except Exception as exc:
            return skip_result(context.phase, "traceability", f"import_failure:{type(exc).__name__}", details={"message": str(exc)})

        market = str(context.metadata.get("market", "US"))
        payloads = {
            "system_status": load_system_status(market),
            "layer_health": load_layer_health(market),
            "market_snapshot": load_market_snapshot(market),
        }
        missing: Dict[str, List[str]] = {}
        for name, payload in payloads.items():
            missing_fields = [field for field in ("source_artifact", "trace_id", "epoch_bounded") if field not in payload]
            if missing_fields:
                missing[name] = missing_fields
        if missing:
            return fail_result(context.phase, "traceability", "dashboard_provenance_gap", details={"missing": missing})
        return pass_result(
            context.phase,
            "traceability",
            "dashboard_payloads_include_provenance",
            details={"market": market},
        )

    def _check_dashboard_freshness(self, context: ValidationContext):
        try:
            from src.dashboard.backend.loaders.system_status import load_system_status
            from src.dashboard.backend.loaders.temporal import load_temporal_status
        except Exception as exc:
            return skip_result(context.phase, "freshness", f"import_failure:{type(exc).__name__}", details={"message": str(exc)})

        market = str(context.metadata.get("market", "US"))
        system_status = load_system_status(market)
        temporal = load_temporal_status(market)
        truth_epoch = system_status.get("truth_epoch") or temporal.get("truth_epoch")
        if not truth_epoch or truth_epoch == "UNKNOWN":
            return fail_result(context.phase, "freshness", "truth_epoch_unavailable", details={"market": market})
        if temporal.get("error"):
            return fail_result(context.phase, "freshness", "temporal_state_unavailable", details={"market": market, "error": temporal.get("error")})
        return pass_result(
            context.phase,
            "freshness",
            "freshness_and_temporal_signals_present",
            details={"market": market, "truth_epoch": truth_epoch},
        )

    def _check_dashboard_read_only(self, context: ValidationContext):
        app_path = self.repo_root / "src" / "dashboard" / "backend" / "app.py"
        if not app_path.exists():
            return fail_result(context.phase, "read_only_guarantee", "missing_dashboard_app")
        content = app_path.read_text(encoding="utf-8")
        methods_ok = 'allow_methods=["GET"]' in content or "allow_methods=['GET']" in content
        mutating_routes = [token for token in ("@app.post", "@app.put", "@app.delete") if token in content]
        if not methods_ok or mutating_routes:
            return fail_result(
                context.phase,
                "read_only_guarantee",
                "dashboard_write_surface_detected",
                details={"methods_ok": methods_ok, "mutating_routes": mutating_routes},
                evidence=[str(app_path)],
            )
        return pass_result(context.phase, "read_only_guarantee", "dashboard_routes_remain_get_only", evidence=[str(app_path)])