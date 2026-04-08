# Portfolio Intelligence Enhanced

## Enhancements now active
1. Mutual fund holdings are enriched with benchmark and provenance metadata.
2. Exposure analytics can consume real underlying holdings when available.
3. Strategy suggestions, risk alerts, and opportunity signals include explainability traces.
4. Refresh orchestration now exposes runtime state, auth mode, and refresh duration.
5. Trend and drift history are available for resilience and value changes.

## Intelligence impact
Look-through exposure now feeds into:
- hidden concentration detection
- factor overexposure detection
- macro sensitivity framing
- sleeve-level resilience interpretation
- dashboard-level exposure visibility

## Honest stagnation behavior
If the repo lacks a cached disclosure or benchmark composition for a fund, the system does not pretend it has real look-through coverage. The exposure path now records whether the result came from:
- real disclosure
- benchmark composition
- fallback approximation
- unavailable real look-through
