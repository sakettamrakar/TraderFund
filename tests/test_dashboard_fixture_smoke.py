"""
Dashboard Fixture Smoke Test (RR-C.4)

Proves that the canonical dashboard backend loaders can start from fixture
artifacts without live data or credentials.  These tests exercise the core
loader functions and the manifest_loader helper to ensure:
  1. Loaders return dict payloads (not None, not exceptions)
  2. Provenance fields are present in every response
  3. Freshness metadata is attached to responses
  4. The manifest_loader can read the pipeline manifest
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from dashboard.backend.loaders.manifest_loader import MANIFEST_PATH


# ── Manifest loader tests ────────────────────────────────────────────────────

class TestManifestLoader:
    """Verify the manifest_loader helper can read fixture manifests."""

    def test_get_manifest_returns_dict_when_present(self):
        if not MANIFEST_PATH.exists():
            pytest.skip("No pipeline manifest present — run daily pipeline first")

        from dashboard.backend.loaders.manifest_loader import get_manifest

        manifest = get_manifest(force_reload=True)
        assert isinstance(manifest, dict), "get_manifest should return a dict"
        assert "entries" in manifest
        assert "market_mode" in manifest

    def test_get_manifest_returns_none_when_absent(self, tmp_path, monkeypatch):
        from dashboard.backend.loaders import manifest_loader

        monkeypatch.setattr(manifest_loader, "MANIFEST_PATH", tmp_path / "nonexistent.json")
        assert manifest_loader.get_manifest(force_reload=True) is None

    def test_freshness_metadata_structure(self):
        from dashboard.backend.loaders.manifest_loader import freshness_metadata

        meta = freshness_metadata("some/artifact/path.json", market_mode="fixture")
        assert "_freshness" in meta
        freshness = meta["_freshness"]
        assert "source_artifact" in freshness
        assert "manifest_status" in freshness
        assert "stale" in freshness

    def test_resolve_artifact_path_for_fixture(self):
        if not MANIFEST_PATH.exists():
            pytest.skip("No pipeline manifest present")

        from dashboard.backend.loaders.manifest_loader import resolve_artifact_path

        # These should exist if the fixture pipeline ran
        path = resolve_artifact_path("fixture_raw")
        if path is not None:
            assert path.exists()


# ── Backend loader smoke tests ───────────────────────────────────────────────

class TestLoaderSmoke:
    """
    Smoke test: each core loader must return a dict and include provenance.
    These tests run against whatever data is on disk (fixture or live).
    """

    @staticmethod
    def _assert_is_dict_with_keys(result, required_keys=None):
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        if required_keys:
            for key in required_keys:
                assert key in result, f"Missing key '{key}' in response"

    def test_system_status(self):
        from dashboard.backend.loaders.system_status import load_system_status

        result = load_system_status("US")
        self._assert_is_dict_with_keys(result, ["source_artifact", "trace_id", "epoch_bounded"])

    def test_layer_health(self):
        from dashboard.backend.loaders.layer_health import load_layer_health

        result = load_layer_health("US")
        self._assert_is_dict_with_keys(result, ["source_artifact", "trace_id", "epoch_bounded"])

    def test_layer_health_freshness(self):
        from dashboard.backend.loaders.layer_health import load_layer_health

        result = load_layer_health("US")
        assert "_freshness" in result, "layer_health should include _freshness metadata"
        freshness = result["_freshness"]
        assert "source_artifact" in freshness
        assert "stale" in freshness

    def test_temporal_status(self):
        from dashboard.backend.loaders.temporal import load_temporal_status

        result = load_temporal_status("US")
        assert isinstance(result, dict)

    def test_provenance_loader(self):
        from dashboard.backend.loaders.provenance import load_truth_epoch_id

        epoch = load_truth_epoch_id()
        assert isinstance(epoch, str)


# ── Pipeline manifest integration ────────────────────────────────────────────

class TestManifestIntegration:
    """Verify the pipeline manifest was generated correctly."""

    def test_manifest_is_valid_json(self):
        if not MANIFEST_PATH.exists():
            pytest.skip("Pipeline manifest not present")

        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        assert "generated_at" in data
        assert "market_mode" in data
        assert "entries" in data
        assert isinstance(data["entries"], list)

    def test_manifest_entries_have_required_fields(self):
        if not MANIFEST_PATH.exists():
            pytest.skip("Pipeline manifest not present")

        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        required_fields = {"artifact_id", "producer", "path", "schema_version", "format", "status"}

        for entry in data["entries"]:
            missing = required_fields - set(entry.keys())
            assert not missing, f"Entry {entry.get('artifact_id')} missing fields: {missing}"

    def test_manifest_fixture_entries_are_present(self):
        if not MANIFEST_PATH.exists():
            pytest.skip("Pipeline manifest not present")

        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if data.get("market_mode") != "fixture":
            pytest.skip("Manifest is not in fixture mode")

        ids = {e["artifact_id"] for e in data["entries"]}
        assert "fixture_raw" in ids
        assert "fixture_processed" in ids
        assert "fixture_us_daily" in ids
