# Semantic Enrichment Specification

**Status:** APPROVED
**Last Updated:** 2026-01-17

## 1. Purpose

Enable grouping and accumulation of events by theme without requiring text analysis in the Trader system.

## 2. Enrichment Fields

These fields are **optional** and assigned by the upstream News/Ingestion layer.

| Field | Type | Example Values | Purpose |
| :--- | :--- | :--- | :--- |
| `semantic_tags` | `List[str]` | `["SUPPLY_CHAIN", "RATES"]` | Thematic grouping for accumulation. |
| `event_type` | `str` | `ECONOMIC_DATA`, `GEOPOLITICAL`, `CORPORATE` | Categorical classification. |
| `expectedness` | `str` | `EXPECTED`, `UNEXPECTED` | Was this event scheduled or a surprise? |

## 3. Trader Adapter Rules

The Trader Adapter (`MarketStoryAdapter`) **MUST**:
1.  Accept these fields from the upstream API.
2.  Pass them through to `Event.payload` **untouched**.
3.  **Never** reinterpret, override, or infer these values.

## 4. Critical Clarifications

| Statement | True/False |
| :--- | :--- |
| Enrichment = Interpretation | **FALSE** |
| Enrichment = Prediction | **FALSE** |
| Enrichment = Grouping Support | **TRUE** |

Semantic enrichment exists **solely** to support the Accumulation Buffer's tag-based grouping. It carries no trading signal.

## 5. Upstream Responsibility

The News Repo is responsible for assigning `semantic_tags` using simple, rule-based logic (e.g., keyword matching, source lookup). No LLM reasoning is required initially.
