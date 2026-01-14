"""Research Output - Config"""
from pathlib import Path

# Report Scopes
SCOPE_US_EQUITIES = "US Equities"

# Data paths
DATA_ROOT = Path("data")
NARRATIVE_PATH = DATA_ROOT / "narratives" / "us"
DIFF_PATH = DATA_ROOT / "narrative_diffs" / "us"
OUTPUT_PATH = DATA_ROOT / "research" / "us"

VERSION = "1.0.0"
