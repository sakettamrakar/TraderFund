# Phase 5: Human-in-the-Loop Diagnostics

An analytical module for interpreting Phase 4 observation logs and generating manager-ready reports.

## Purpose
This module supports human judgment, not replaces it. It:
- Analyzes signal quality patterns
- Compares "what-if" filters WITHOUT applying them
- Produces a concise, decision-ready report

## Usage
```python
from analysis.phase5_diagnostics import ManagerReportGenerator

generator = ManagerReportGenerator()
report = generator.generate_report(output_path="reports/diagnostic_report.md")
print(report)
```

## Module Components
- `loader.py`: Loads and validates Phase 4 observation CSVs.
- `metrics.py`: Computes core quality metrics (A/B ratio, frequency, etc.).
- `clustering.py`: Groups signals by time-of-day buckets.
- `simulations.py`: Runs virtual "what-if" filters (analytical only).
- `report_generator.py`: Produces the final Markdown report.

## Constraints
- DOES NOT modify momentum engine logic.
- DOES NOT auto-tune parameters.
- DOES NOT optimize thresholds.

All decisions remain with the human trader.
