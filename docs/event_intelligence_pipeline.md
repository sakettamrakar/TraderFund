# Event Intelligence Pipeline

## Runtime flow
1. Trader News API or cached story file is read by the event-intelligence bridge.
2. Stories are normalized using the existing `MarketStory` contract.
3. Entity mapping links stories to holdings.
4. Portfolio relevance is determined from current holdings.
5. Stock research profiles receive event intelligence fields.
6. Portfolio analytics emits:
   - `news_adapter_status`
   - `portfolio_event_alerts`
   - `portfolio_event_timeline`
7. Dashboard panels display adapter status, event alerts, stock event timelines, and event-aware research narratives.

## Validation labels
- `NEWS_ADAPTER_OK`
- `ENTITY_MAPPING_OK`
- `NARRATIVE_LAYER_OK`
- `PORTFOLIO_EVENT_LINKAGE_OK`
- `DASHBOARD_EVENT_DISPLAY_OK`
