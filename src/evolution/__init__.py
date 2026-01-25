# Evolution Package
"""
Evolution Package (L12 - Evolution Phase).
Provides strategy evaluation, diagnostics, and visibility tools.

SAFETY: This package enables LEARNING and DEBUGGING, not EXECUTION.
All real market interaction is FORBIDDEN.
Evolution is about understanding reality, not forcing performance.
"""
from .bulk_evaluator import BulkEvaluator, StrategyEvaluationResult
from .replay_engine import ReplayEngine, ReplayResult, ReplayStep
from .paper_pnl import PaperPnLCalculator, PaperPnL, PaperTrade
from .coverage_diagnostics import CoverageDiagnostics, RegimeCoverage, FactorCoverage, CoverageStatus
from .rejection_analysis import RejectionAnalyzer, RejectionEntry, RejectionCategory, StrategyRejectionStats

__all__ = [
    # Bulk evaluation
    "BulkEvaluator",
    "StrategyEvaluationResult",
    # Replay
    "ReplayEngine",
    "ReplayResult",
    "ReplayStep",
    # Paper P&L
    "PaperPnLCalculator",
    "PaperPnL",
    "PaperTrade",
    # Coverage diagnostics
    "CoverageDiagnostics",
    "RegimeCoverage",
    "FactorCoverage",
    "CoverageStatus",
    # Rejection analysis
    "RejectionAnalyzer",
    "RejectionEntry",
    "RejectionCategory",
    "StrategyRejectionStats",
]
