# Severity Mapping Specification

**Status: FROZEN (v1.0)**
**Last Updated:** 2026-01-17

This document defines the **canonical mapping** between upstream severity hints and downstream numerical scores for the Narrative Genesis Engine.

## 1. Canonical Mapping (Exact)

These values are **HEURISTIC MAGNITUDES**, not probabilities or predictions.

| Severity Hint | Score | Rationale |
| :--- | :--- | :--- |
| **LOW** | **40.0** | **Below Genesis Threshold (60.0).** Represents noise or minor updates. Default state. |
| **MEDIUM** | **70.0** | **Above Genesis Threshold.** Represents standard, attention-worthy news events. |
| **HIGH** | **90.0** | **Significantly Above Threshold.** Represents major, disruptive, or critical events. |

## 2. Rationale

- **Low (40.0):** Deliberately set well below the default genesis threshold (60.0) to ensure high-pass filtering of noise.
- **Medium (70.0):** Provides a comfortable buffer above the threshold (10 points) to ensure "Standard" news is reliably captured.
- **High (90.0):** Set near the ceiling (100.0) to maximize initial confidence and ensure immediate visibility.

## 3. Extension Rules

1.  **New Severity Levels:** Introduction of new levels (e.g., `CRITICAL`, `FLASH`) requires a formal revision of this spec.
2.  **Threshold Tuning:** The Genesis Engine threshold (currently 60.0) may change, but these mapping values should remain stable to preserve historical consistency.
3.  **No Dynamic Tuning:** These values must NOT be auto-tuned or dynamically adjusted by the system. They are fixed constants.
