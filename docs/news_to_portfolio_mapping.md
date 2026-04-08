# News to Portfolio Mapping

## Mapping logic
The event bridge maps news to holdings using:
- ticker aliases
- normalized holding names
- manual entity aliases for known cases such as `Hindustan Aeronautics -> HAL` and `ASML -> ASML`
- optional upstream `mentioned_entities`
- optional upstream `semantic_tags`

## Portfolio relevance rule
If a mapped ticker is present in current portfolio holdings, the event is marked portfolio-relevant and propagated into:
- stock research profiles
- portfolio event alerts
- portfolio event timeline
- synthesized portfolio narrative

## Honest stagnation
If no Trader News feed or cache is available, the adapter status is surfaced explicitly rather than silently implying event coverage.
