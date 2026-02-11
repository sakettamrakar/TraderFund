
import sys
import logging
from pathlib import Path
from agents import component_agent

# Redirect stdout to file
sys.stdout = open("debug_agent_output.txt", "w", encoding="utf-8")
sys.stderr = sys.stdout

print("Starting Debug Run...")

# Check Path resolution
PROJECT_ROOT = Path("c:/GIT/TraderFund") # Hardcoded for test
action_plan_path = PROJECT_ROOT / "automation/tasks/action_plan.json"
print(f"Checking Plan Path: {action_plan_path}")
if action_plan_path.exists():
    print(f"Plan Exists. Content: {action_plan_path.read_text(encoding='utf-8')[:100]}...")
else:
    print("Plan Missing!")

sys.path.insert(0, "automation") 
# We need to import correctly for component_agent which expects certain sys.path
# component_agent is in automation/agents/
from agents import component_agent
# Force PROJECT_ROOT in component_agent? It uses __file__.
print(f"ComponentAgent PROJECT_ROOT: {component_agent.PROJECT_ROOT}")

try:
    output = component_agent.run([])
    print(f"Agent Output: {output}")

except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print("Debug Run Complete.")
