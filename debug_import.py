import sys
import os
print(f"PYTHONPATH: {sys.path}")
print(f"CWD: {os.getcwd()}")

try:
    import narratives.core.enums
    print("SUCCESS: import narratives.core.enums")
except Exception as e:
    print(f"FAILURE: import narratives.core.enums : {e}")

try:
    import traderfund.narrative.adapters.market_story_adapter
    print("SUCCESS: import traderfund.narrative.adapters.market_story_adapter")
except Exception as e:
    print(f"FAILURE: import traderfund.narrative.adapters.market_story_adapter : {e}")
