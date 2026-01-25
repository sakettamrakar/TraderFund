"""
##############################################################################
## PAPER TRADING ANALYTICS - READ ONLY
##############################################################################
Plots

On-demand visualization generation.
Plots are saved locally, never auto-opened.
##############################################################################
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Default output directory
DEFAULT_PLOT_DIR = Path("paper_trading/analytics/plots")


def generate_equity_curve(
    df: pd.DataFrame,
    output_dir: Optional[Path] = None,
    filename: str = "equity_curve.png",
) -> Optional[Path]:
    """Generate equity curve plot.

    Args:
        df: Trade DataFrame with net_pnl column.
        output_dir: Directory to save plot.
        filename: Output filename.

    Returns:
        Path to saved plot, or None if failed.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return None

    if df.empty or "net_pnl" not in df.columns:
        logger.warning("No data for equity curve")
        return None

    output_dir = output_dir or DEFAULT_PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    cumulative = df["net_pnl"].cumsum()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(len(cumulative)), cumulative, linewidth=2)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel("Trade Number")
    ax.set_ylabel("Cumulative P&L (Paper)")
    ax.set_title("Paper Trading Equity Curve")
    ax.grid(True, alpha=0.3)

    filepath = output_dir / filename
    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)

    logger.info(f"Saved equity curve: {filepath}")
    return filepath


def generate_return_distribution(
    df: pd.DataFrame,
    output_dir: Optional[Path] = None,
    filename: str = "return_distribution.png",
) -> Optional[Path]:
    """Generate trade return distribution histogram.

    Args:
        df: Trade DataFrame with net_pnl column.
        output_dir: Directory to save plot.
        filename: Output filename.

    Returns:
        Path to saved plot, or None if failed.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return None

    if df.empty or "net_pnl" not in df.columns:
        return None

    output_dir = output_dir or DEFAULT_PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df["net_pnl"], bins=20, edgecolor='black', alpha=0.7)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
    ax.set_xlabel("P&L per Trade")
    ax.set_ylabel("Frequency")
    ax.set_title("Trade Return Distribution (Paper)")
    ax.grid(True, alpha=0.3)

    filepath = output_dir / filename
    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)

    logger.info(f"Saved distribution plot: {filepath}")
    return filepath


def generate_trades_by_hour(
    df: pd.DataFrame,
    output_dir: Optional[Path] = None,
    filename: str = "trades_by_hour.png",
) -> Optional[Path]:
    """Generate trades per hour bar chart.

    Args:
        df: Trade DataFrame with timestamp column.
        output_dir: Directory to save plot.
        filename: Output filename.

    Returns:
        Path to saved plot, or None if failed.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("matplotlib not available, skipping plot")
        return None

    if df.empty or "timestamp" not in df.columns:
        return None

    output_dir = output_dir or DEFAULT_PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    df = df.copy()
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    hour_counts = df["hour"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(hour_counts.index, hour_counts.values, edgecolor='black', alpha=0.7)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Number of Trades")
    ax.set_title("Trades by Hour (Paper)")
    ax.set_xticks(range(9, 16))
    ax.grid(True, alpha=0.3, axis='y')

    filepath = output_dir / filename
    fig.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)

    logger.info(f"Saved trades by hour: {filepath}")
    return filepath


def generate_all_plots(df: pd.DataFrame, output_dir: Optional[Path] = None) -> dict:
    """Generate all available plots.

    Args:
        df: Trade DataFrame.
        output_dir: Directory to save plots.

    Returns:
        Dict mapping plot name to filepath.
    """
    results = {}

    path = generate_equity_curve(df, output_dir)
    if path:
        results["equity_curve"] = path

    path = generate_return_distribution(df, output_dir)
    if path:
        results["return_distribution"] = path

    path = generate_trades_by_hour(df, output_dir)
    if path:
        results["trades_by_hour"] = path

    return results
