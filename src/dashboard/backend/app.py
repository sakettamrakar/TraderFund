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
async def get_system_status():
    return load_system_status()

@app.get("/api/layers/health")
async def get_layer_health():
    return load_layer_health()

@app.get("/api/market/snapshot")
async def get_market_snapshot():
    return load_market_snapshot()

@app.get("/api/watchers/timeline")
async def get_watcher_timeline(limit: int = 10):
    return load_watcher_timeline(limit)

@app.get("/api/strategies/eligibility")
async def get_strategy_eligibility():
    return load_strategy_eligibility()

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
async def get_capital_readiness():
    return load_capital_readiness()

@app.get("/api/capital/history")
async def get_capital_history():
    return load_capital_history()

from dashboard.backend.loaders.macro import load_macro_context
@app.get("/api/macro/context")
async def get_macro_context():
    return load_macro_context()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
