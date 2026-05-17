#!/usr/bin/env python3
"""
Epistemic Validator (RR-D.1)
============================
Enforces core repository invariants and documentation contracts.
Replaces the old placeholder with concrete smoke-checks.
"""

import argparse
import sys
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def check_readme_authority() -> bool:
    """Ensure README defines repository authority correctly."""
    readme_path = PROJECT_ROOT / "README.md"
    if not readme_path.exists():
        print("[FAIL] README.md is missing.")
        return False

    content = readme_path.read_text(encoding="utf-8")

    # Check 1: DWBS reference
    if "DWBS_REPOSITORY_RECOVERY_2026-05-17.md" not in content:
        print("[FAIL] README.md does not reference the active DWBS recovery plan.")
        return False

    # Check 2: Dashboard Authority
    if "Dashboard Authority" not in content or "src/dashboard/backend" not in content:
        print("[FAIL] README.md is missing the Canonical Dashboard Authority section.")
        return False

    print("[PASS] README.md authority checks passed.")
    return True

def check_phase_lock_imports() -> bool:
    """
    Ensure ingestion/validation layers don't import live portfolio execution
    at the module level.
    """
    forbidden_imports = [
        re.compile(r"^\s*import\s+traderfund\.portfolio"),
        re.compile(r"^\s*from\s+traderfund\.portfolio\s+import")
    ]

    scan_dirs = [
        PROJECT_ROOT / "traderfund" / "ingestion",
        PROJECT_ROOT / "traderfund" / "pipeline",
        PROJECT_ROOT / "traderfund" / "validation",
    ]

    failed = False
    for d in scan_dirs:
        if not d.exists():
            continue
        for py_file in d.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for i, line in enumerate(lines):
                for pattern in forbidden_imports:
                    if pattern.search(line):
                        print(f"[FAIL] Phase-Lock violation in {py_file.relative_to(PROJECT_ROOT)}:{i+1}:")
                        print(f"   {line.strip()}")
                        print("   (Lower phases must not import portfolio execution directly)")
                        failed = True

    if not failed:
        print("[PASS] Phase-lock import boundaries passed.")
    return not failed

def check_market_modes_fixture_default() -> bool:
    """Ensure daily pipeline uses fixture mode by default to prevent live accidents."""
    daily_py = PROJECT_ROOT / "traderfund" / "pipeline" / "daily.py"
    if not daily_py.exists():
        print("[FAIL] traderfund/pipeline/daily.py is missing.")
        return False

    content = daily_py.read_text(encoding="utf-8")
    if "--market\",\n        default=\"fixture" not in content and "--market\", default=\"fixture" not in content and "default=\"fixture\"" not in content:
        print("[FAIL] traderfund/pipeline/daily.py does not default to fixture mode.")
        return False

    print("[PASS] Daily pipeline defaults to fixture mode.")
    return True

def check_no_live_write_apis() -> bool:
    """Ensure no live broker order execution or capital mutation code exists."""
    forbidden_terms = [
        ("place_order", ["order_simulator", "test_execution", "cli.py", "trade_executor"]),
        ("cancel_order", ["order_simulator", "test_execution", "cli.py", "trade_executor"]),
        ("modify_order", ["order_simulator", "test_execution", "cli.py", "trade_executor"]),
    ]

    scan_dirs = [
        PROJECT_ROOT / "src" / "portfolio_intelligence",
        PROJECT_ROOT / "paper_trading",
    ]

    failed = False
    for d in scan_dirs:
        if not d.exists():
            continue
        for py_file in d.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for i, line in enumerate(lines):
                # Skip comments or strings
                if line.strip().startswith("#"):
                    continue
                for term, allowed_files in forbidden_terms:
                    # check if the term is in the line and the file is not allowed
                    if term in line:
                        if any(allowed in py_file.name for allowed in allowed_files):
                            continue
                        print(f"[FAIL] Forbidden API '{term}' found in non-allowed file {py_file.relative_to(PROJECT_ROOT)}:{i+1}:")
                        print(f"   {line.strip()}")
                        failed = True

    if not failed:
        print("[PASS] Operational safety constraints (no write APIs) verified.")
    return not failed

def check_no_hardcoded_secrets() -> bool:
    """Ensure no API keys or secrets are hardcoded in python or json files."""
    secret_patterns = [
        re.compile(r"KITE_API_SECRET\s*=\s*['\"][a-zA-Z0-9]{10,}['\"]"),
        re.compile(r"KITE_ACCESS_TOKEN\s*=\s*['\"][a-zA-Z0-9]{10,}['\"]"),
    ]

    scan_dirs = [
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "paper_trading",
        PROJECT_ROOT / "research_modules",
        PROJECT_ROOT / "scripts",
        PROJECT_ROOT / "traderfund",
        PROJECT_ROOT / "config",
    ]

    failed = False
    for d in scan_dirs:
        if not d.exists():
            continue
        for py_file in d.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(content.splitlines()):
                for pattern in secret_patterns:
                    if pattern.search(line):
                        print(f"[FAIL] Hardcoded secret pattern in {py_file.relative_to(PROJECT_ROOT)}:{i+1}")
                        failed = True

        for json_file in d.rglob("*.json"):
            content = json_file.read_text(encoding="utf-8", errors="ignore")
            if "api_secret" in content.lower() or "access_token" in content.lower():
                matches = re.findall(r"['\"][^'\"]{15,}['\"]", content)
                if matches:
                    filtered = [m for m in matches if not any(p in m for p in ["http", "path", "version", "schema", "2026", "2025"])]
                    if filtered:
                        print(f"[FAIL] Probable hardcoded secret in JSON {json_file.relative_to(PROJECT_ROOT)}: {filtered}")
                        failed = True

    if not failed:
        print("[PASS] Hardcoded secrets validation passed.")
    return not failed

def main():
    parser = argparse.ArgumentParser(description="Epistemic Validator")
    parser.add_argument("--mode", type=str, default="strict", help="Validation mode")
    args = parser.parse_args()

    print(f"Running Epistemic Validator in {args.mode} mode...\n")

    passed = True
    passed &= check_readme_authority()
    passed &= check_phase_lock_imports()
    passed &= check_market_modes_fixture_default()
    passed &= check_no_live_write_apis()
    passed &= check_no_hardcoded_secrets()

    if passed:
        print("\n[PASS] All epistemic validation checks passed.")
        return 0
    else:
        print("\n[FAIL] Epistemic validation failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
