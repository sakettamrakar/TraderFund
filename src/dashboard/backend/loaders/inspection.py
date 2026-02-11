from pathlib import Path
import re
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
REPORT_PATH = PROJECT_ROOT / "docs" / "audit" / "phase_3_stress_scenario_report.md"

def load_stress_scenarios() -> Dict[str, Any]:
    """
    Parses the Phase 3 Stress Scenario Report into a structured JSON for inspection mode.
    """
    if not REPORT_PATH.exists():
        return {"error": "Stress report not found", "scenarios": []}
    
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    scenarios = []
    current_scenario = None
    current_market = None
    
    # Metadata extraction
    trace = {
        "source": "docs/audit/phase_3_stress_scenario_report.md",
        "epoch": "UNKNOWN",
        "mode": "UNKNOWN"
    }

    scenario_regex = re.compile(r"^## (S\d+): (.+)")
    market_regex = re.compile(r"^### ([A-Z]+)")
    key_val_regex = re.compile(r"^- ([^:]+): (.+)")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse Header Meta
        if line.startswith("Epoch:"):
            trace["epoch"] = line.split(":", 1)[1].strip()
        if line.startswith("Execution Mode:"):
            trace["mode"] = line.split(":", 1)[1].strip()
            
        # Scenario Header
        m_scen = scenario_regex.match(line)
        if m_scen:
            # Save previous if exists
            if current_scenario:
                scenarios.append(current_scenario)
            
            sid = m_scen.group(1)
            name = m_scen.group(2)
            current_scenario = {
                "id": sid,
                "name": name,
                "condition_desc": "",
                "markets": {}
            }
            current_market = None
            continue
            
        # Market Header
        m_mkt = market_regex.match(line)
        if m_mkt:
            current_market = m_mkt.group(1)
            if current_scenario:
                current_scenario["markets"][current_market] = {"inputs": {}, "outcomes": {}}
            continue
            
        # Condition
        if line.startswith("Condition:") and current_scenario:
            current_scenario["condition_desc"] = line.split(":", 1)[1].strip()
            continue
            
        # Key-Value Pairs
        m_kv = key_val_regex.match(line)
        if m_kv and current_scenario:
            key = m_kv.group(1).strip()
            val = m_kv.group(2).strip()
            
            # Helper to parse list strings like "['A', 'B']"
            if val.startswith("[") and val.endswith("]"):
                try:
                    import ast
                    val = ast.literal_eval(val)
                except:
                    pass
            
            if current_market:
                # Inside a market block
                target = current_scenario["markets"][current_market]
                if key == "Input":
                     # Parse Input like "VIX=40.0" -> {"VIX": 40.0}
                     if "=" in val:
                         k, v = val.split("=", 1)
                         try: v = float(v) 
                         except: pass
                         target["inputs"][k.strip()] = v
                     else:
                         target["inputs"]["raw"] = val
                         
                elif key in ["Result Stress State", "Policy State", "Constraints", "Blocked Actions", "Permissions"]:
                    target["outcomes"][key.lower().replace(" ", "_")] = val
                    
                elif key == "VERDICT":
                    target["verdict"] = val
            else:
                # Scenario level check? usually explicitly market scoped in report
                pass

    # Append last scenario
    if current_scenario:
        scenarios.append(current_scenario)
        
    return {
        "trace": trace,
        "scenarios": scenarios
    }
