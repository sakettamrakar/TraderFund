# Regime Diagnostics Bundle

**Generated**: 2026-01-25T09:05:22.001377

**Overall Status**: SUCCESS

## Component Status

| Component | Status | Summary |
|:----------|:-------|:--------|
| symbol_enumeration | ✅ SUCCESS | 7 symbols enumerated |
| ingestion_coverage | ✅ SUCCESS | Present: 7, Missing: 0 |
| depth_audit | ✅ SUCCESS | Sufficient: 7, Insufficient: 0 |
| alignment_audit | ✅ SUCCESS | Aligned: 21, Misaligned: 0 |
| viability_check | ✅ SUCCESS | VIABLE |
| undefined_attribution | ✅ SUCCESS | 0 undefined attributed |

## Artifact Locations

| Artifact | Path |
|:---------|:-----|
| Symbol Matrix | `docs\diagnostics\regime/symbol_coverage_matrix.csv` |
| Coverage Report | `docs\diagnostics\regime/ingestion_coverage_report.csv` |
| Sufficiency Report | `docs\diagnostics\regime/lookback_sufficiency_report.md` |
| Alignment Report | `docs\diagnostics\regime/temporal_alignment_report.md` |
| Viability Report | `docs\diagnostics\regime/state_viability_report.md` |
| Attribution Table | `docs\diagnostics\regime/undefined_regime_attribution.csv` |

## Next Steps

1. All audits passed
2. Regime logic tuning is eligible (pending authorization)
