from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard.backend.loaders.system_status import load_system_status
from dashboard.backend.loaders.layer_health import load_layer_health
from dashboard.backend.loaders.market_snapshot import load_market_snapshot
from dashboard.backend.loaders.watchers import load_watcher_timeline
from dashboard.backend.loaders.strategies import load_strategy_eligibility
from dashboard.backend.loaders.meta_summary import load_meta_summary
from dashboard.backend.loaders.narrative import load_system_narrative, load_system_blockers
from dashboard.backend.loaders.capital import load_capital_readiness, load_capital_history

app = FastAPI(title="TraderFund Market Intelligence Dashboard", version="1.0.0")

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET"], # STRICTLY READ-ONLY
    allow_headers=["*"],
)

@app.get("/api/system/status")
async def get_system_status(market: str = "US"):
    return load_system_status(market)

@app.get("/api/layers/health")
async def get_layer_health(market: str = "US"):
    return load_layer_health(market)

@app.get("/api/market/snapshot")
async def get_market_snapshot(market: str = "US"):
    return load_market_snapshot(market)

@app.get("/api/watchers/timeline")
async def get_watcher_timeline(market: str = "US", limit: int = 10):
    return load_watcher_timeline(market, limit)

@app.get("/api/strategies/eligibility")
async def get_strategy_eligibility(market: str = "US"):
    return load_strategy_eligibility(market)

@app.get("/api/meta/summary")
async def get_meta_summary():
    return load_meta_summary()

@app.get("/api/system/narrative")
async def get_system_narrative():
    return load_system_narrative()

@app.get("/api/system/blockers")
async def get_system_blockers():
    return load_system_blockers()

@app.get("/api/system/activation_conditions")
async def get_activation_conditions():
    """
    Static epistemic rules defining what is required for activation.
    """
    return {
        "momentum": [
            "ExpansionTransition != NONE",
            "DispersionBreakout != NONE",
            "MomentumEmergence != NONE"
        ]
    }

@app.get("/api/capital/readiness")
async def get_capital_readiness(market: str = "US"):
    return load_capital_readiness(market)

@app.get("/api/capital/history")
async def get_capital_history(market: str = "US"):
    return load_capital_history(market)

from dashboard.backend.loaders.macro import load_macro_context
@app.get("/api/macro/context")
async def get_macro_context(market: str = "US"):
    return load_macro_context(market)

from dashboard.backend.loaders.intelligence import load_intelligence_snapshot, load_decision_policy, load_fragility_context, load_execution_gate, load_stress_posture, load_constraint_posture, load_evaluation_scope, load_market_parity
@app.get("/api/intelligence/gate")
async def get_execution_gate():
    """
    Returns the canonical Execution Gate Status (A1.2).
    """
    return load_execution_gate()

@app.get("/api/intelligence/parity/{market}")
async def get_market_parity(market: str = "US"):
    return load_market_parity(market)

@app.get("/api/meta/evaluation/scope")
async def get_evaluation_scope():
    return load_evaluation_scope()

@app.get("/api/intelligence/stress_posture")
async def get_stress_posture():
    return load_stress_posture()

@app.get("/api/intelligence/constraint_posture")
async def get_constraint_posture():
    return load_constraint_posture()

@app.get("/api/intelligence/snapshot")
async def get_intelligence_snapshot(market: str = "US"):
    return load_intelligence_snapshot(market)

@app.get("/api/intelligence/policy/{market}")
async def get_policy_decision(market: str = "US"):
    """
    Returns the Governance Decision Policy for the market.
    """
    return load_decision_policy(market)

@app.get("/api/intelligence/fragility/{market}")
async def get_fragility_context(market: str = "US"):
    """
    Returns the Systemic Fragility/Stress context for the market.
    """
    return load_fragility_context(market)

from dashboard.backend.loaders.data_anchor import load_data_anchor
@app.get("/api/data_anchor")
async def get_data_anchor(market: str = "US"):
    """
    EPISTEMIC RESTORATION: Data Anchor endpoint.
    Returns Truth Epoch, Data Provenance, and Confidence for the specified market.
    """
    return load_data_anchor(market)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
