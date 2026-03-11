from src.layers.portfolio_intelligence import build_portfolio_intelligence_blueprint


def test_portfolio_intelligence_blueprint_governance_contract():
    blueprint = build_portfolio_intelligence_blueprint()

    assert blueprint.truth_epoch == "TRUTH_EPOCH_2026-03-06_01"
    assert blueprint.frozen_epoch is True
    assert blueprint.data_mode == "REAL_ONLY"
    assert blueprint.execution_mode == "DRY_RUN"
    assert blueprint.markets == ("US", "INDIA")
    assert blueprint.invariants == (
        "INV-NO-EXECUTION",
        "INV-NO-CAPITAL",
        "INV-NO-SELF-ACTIVATION",
        "INV-PROXY-CANONICAL",
        "INV-READ-ONLY-DASHBOARD",
    )
    assert blueprint.obligations == (
        "OBL-DATA-PROVENANCE-VISIBLE",
        "OBL-TRUTH-EPOCH-DISCLOSED",
        "OBL-REGIME-GATE-EXPLICIT",
        "OBL-MARKET-PARITY",
        "OBL-HONEST-STAGNATION",
    )


def test_portfolio_intelligence_blueprint_dashboard_is_read_only():
    blueprint = build_portfolio_intelligence_blueprint()

    assert blueprint.dashboard.truth_epoch_visible is True
    assert blueprint.dashboard.provenance_visible is True
    assert blueprint.dashboard.module_name == "Portfolio Intelligence"
    assert len(blueprint.dashboard.endpoints) == 9
    assert all(endpoint.method == "GET" for endpoint in blueprint.dashboard.endpoints)
    assert all(endpoint.read_only for endpoint in blueprint.dashboard.endpoints)


def test_portfolio_intelligence_blueprint_is_deterministic():
    first = build_portfolio_intelligence_blueprint()
    second = build_portfolio_intelligence_blueprint()

    assert first.as_dict() == second.as_dict()
    assert first.blueprint_hash == second.blueprint_hash
