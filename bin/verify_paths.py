from pathlib import Path
import os

# Simulate api.py location: c:\GIT\TraderFund\src\dashboard\backend\api.py
# If running from c:\GIT\TraderFund, verify relative paths.

# Logic from api.py
# BASE_DIR = Path(__file__).parent.parent.parent.parent 
# But here we are in bin/verify_paths.py
# so BASE_DIR is parent.parent

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
EV_DIR = DOCS_DIR / "evolution"
TICKS_DIR = EV_DIR / "ticks"

print(f"BASE_DIR: {BASE_DIR}")
print(f"TICKS_DIR: {TICKS_DIR}")
if TICKS_DIR.exists():
    print(f"TICKS_DIR exists.")
    ticks = list(TICKS_DIR.iterdir())
    print(f"Count: {len(ticks)}")
    if len(ticks) > 0:
        print(f"First tick: {ticks[0]}")
else:
    print("TICKS_DIR DOES NOT EXIST")
