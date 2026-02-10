"""
System Health Check (Smoke Test)
=================================
Answers ONE question: "Can the system still run end-to-end at a basic level?"

- No network calls
- No production configuration assumed
- No new dependencies
- Read-only: does not modify any state

Usage:
    python healthcheck.py
"""

import sys
import traceback


def check_core_imports():
    """Verify that core modules can be imported without error."""
    import pandas as pd
    import numpy as np
    from pathlib import Path
    return True


def check_momentum_engine():
    """
    Instantiate MomentumEngine and run generate_signals_from_df
    with synthetic data. Verifies the core signal pipeline works
    without requiring real market data or network access.
    """
    import pandas as pd
    import numpy as np

    # Add src to path for imports
    sys.path.insert(0, "src")
    from core_modules.momentum_engine.momentum_engine import MomentumEngine

    engine = MomentumEngine(processed_data_path="__nonexistent__")

    # Build synthetic 1-minute OHLCV data (30 candles, one trading day)
    # Designed to trigger a momentum signal: rising price, expanding volume, near HOD
    n = 30
    base_price = 100.0
    timestamps = pd.date_range("2026-01-15 09:30", periods=n, freq="1min")

    prices = base_price + np.linspace(0, 5, n)  # steady uptrend
    noise = np.random.RandomState(42).uniform(-0.1, 0.1, n)
    prices = prices + noise

    volumes = np.full(n, 1000, dtype=float)
    volumes[-5:] = 5000  # volume surge at end

    df = pd.DataFrame({
        "timestamp": timestamps,
        "open":  prices - 0.1,
        "high":  prices + 0.2,
        "low":   prices - 0.3,
        "close": prices,
        "volume": volumes,
    })

    # Run the engine — should NOT throw
    signals = engine.generate_signals_from_df(df, symbol="HEALTH_TEST", exchange="TEST")

    # signals is a list (may be empty — that's fine, we care about no-crash)
    assert signals is not None, "generate_signals_from_df returned None"
    assert isinstance(signals, list), f"Expected list, got {type(signals)}"

    return len(signals)


def check_memory_audit():
    """Verify the memory audit script can be imported and its helpers work."""
    sys.path.insert(0, "scripts")
    import importlib
    mod = importlib.import_module("memory_audit")

    # Exercise read-only helpers
    files = mod.collect_memory_files()
    assert files is not None, "collect_memory_files returned None"
    assert len(files) > 0, "No memory files found"

    return len(files)


def check_data_files_exist():
    """Verify that at least one canonical data file exists."""
    from pathlib import Path

    data_dirs = [
        Path("data/us_market"),
        Path("data/india_market"),
    ]
    found = 0
    for d in data_dirs:
        if d.exists():
            csvs = list(d.glob("*.csv"))
            found += len(csvs)

    assert found > 0, "No CSV data files found in data/us_market or data/india_market"
    return found


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    checks = [
        ("Core Imports",        check_core_imports),
        ("Momentum Engine",     check_momentum_engine),
        ("Memory Audit",        check_memory_audit),
        ("Data Files Present",  check_data_files_exist),
    ]

    all_ok = True
    results = []

    for name, fn in checks:
        try:
            result = fn()
            msg = f"  ✅ {name}: OK"
            if isinstance(result, int):
                msg += f" ({result} items)"
            results.append(msg)
        except Exception as e:
            all_ok = False
            results.append(f"  ❌ {name}: FAILED — {e}")
            traceback.print_exc(file=sys.stderr)

    print()
    print("=" * 50)
    print("  SYSTEM HEALTH CHECK")
    print("=" * 50)
    for r in results:
        print(r)
    print("-" * 50)

    if all_ok:
        print("  HEALTH OK")
    else:
        print("  HEALTH DEGRADED — see failures above")

    print()
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
