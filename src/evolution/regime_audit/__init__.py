# Regime Audit Package
"""
Regime Audit Package (L12 - Evolution Phase / Regime Subsystem).
Provides regime observability audit tools.

SAFETY: This package is READ-ONLY.
It does not modify data, logic, or thresholds.
It diagnoses why regime = undefined occurs.
"""
from .symbol_enumeration import SymbolEnumeration, RequiredSymbol, SymbolRole
from .ingestion_coverage import IngestionCoverageAudit, SymbolCoverage, CoverageStatus
from .depth_audit import DepthAudit, LookbackSufficiency, SufficiencyStatus, HistoricalGap
from .alignment_audit import AlignmentAudit, SymbolAlignment, AlignmentStatus, AlignmentGap
from .viability_check import StateViabilityCheck, ViabilityCheck, ViabilityStatus, BlockingReason
from .undefined_attribution import UndefinedAttributionReport, UndefinedAttribution, UndefinedCause

__all__ = [
    # Symbol enumeration
    "SymbolEnumeration",
    "RequiredSymbol",
    "SymbolRole",
    # Ingestion coverage
    "IngestionCoverageAudit",
    "SymbolCoverage",
    "CoverageStatus",
    # Depth audit
    "DepthAudit",
    "LookbackSufficiency",
    "SufficiencyStatus",
    "HistoricalGap",
    # Alignment audit
    "AlignmentAudit",
    "SymbolAlignment",
    "AlignmentStatus",
    "AlignmentGap",
    # Viability check
    "StateViabilityCheck",
    "ViabilityCheck",
    "ViabilityStatus",
    "BlockingReason",
    # Undefined attribution
    "UndefinedAttributionReport",
    "UndefinedAttribution",
    "UndefinedCause",
]
