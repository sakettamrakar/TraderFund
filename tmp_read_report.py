import os, json
ticks = sorted([d for d in os.listdir("docs/evolution/ticks") if d.startswith("tick_")], reverse=True)
latest = ticks[0]
print(f"Latest tick: {latest}")

for market in ["US", "INDIA"]:
    rc_path = f"docs/evolution/ticks/{latest}/{market}/regime_context.json"
    if os.path.exists(rc_path):
        rc = json.load(open(rc_path))
        ctx = rc.get("regime_context", {})
        regime = ctx.get("regime")
        state = ctx.get("canonical_state")
        print(f"  [{market}] Regime: {regime} | Canonical: {state}")

    fc_path = f"docs/evolution/ticks/{latest}/{market}/factor_context.json"
    if os.path.exists(fc_path):
        fc = json.load(open(fc_path))
        ctx = fc.get("factor_context", {})
        suff = ctx.get("sufficiency", {}).get("status")
        factors = ctx.get("factors", {})
        mom = factors.get("momentum", {}).get("level", {}).get("state", "UNKNOWN")
        vol = factors.get("volatility", {}).get("level", 0.0)
        liq = factors.get("liquidity", {}).get("state", "UNKNOWN")
        print(f"  [{market}] Sufficiency: {suff} | Mom: {mom} | Vol: {vol:.2f} | Liq: {liq}")

    mc_path = f"docs/evolution/ticks/{latest}/{market}/macro_context.json"
    if os.path.exists(mc_path):
        mc = json.load(open(mc_path))
        stress = mc.get("stress_level", "UNKNOWN")
        rates = mc.get("rates_trend", "UNKNOWN")
        print(f"  [{market}] Macro Stress: {stress} | Rates Trend: {rates}")
