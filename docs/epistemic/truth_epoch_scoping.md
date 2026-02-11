# Truth Epoch & Proxy Definition

## 1. Problem Definition
A `Truth Epoch` (snapshot of reality) is meaningless without knowing *which* Proxy Set generated it.
If we swap `SPY` for `VTI` in the US Proxy Set, the "Truth" of `MOMENTUM=BULLISH` might flip to `BEARISH` even if prices didn't change.
Therefore, Truth is relative to the Definition (Proxy Set).

---

## 2. Definition Rules

### Rule 1: Version Lock
Every `truth_epoch.json` MUST include the version hash or ID of the `MarketProxySet` used to generate it.
```json
"validity_context": {
    "market": "US",
    "proxy_set_version": "1.0.0",
    "proxy_status": "CANONICAL"
}
```

### Rule 2: Invalidation on Definition Change
If the `MarketProxySet` definition changes (e.g. adding `IWM`), the previous Truth Epoch is **INVALIDATED** for forward-prospective decision making. A new Epoch must be computed.

### Rule 3: Historical Preservation
Old definitions and their resulting epochs are preserved in the `evolution/` log. We do not rewrite history effectively, we acknowledge that *under Definition v1.0, the world looked like X*.

---

## 3. Implementation Plan
1.  **Proxy Set Versioning**: Assign Semantic Versioning to `market_proxy_sets.json`.
2.  **Epoch Metadata**: Update `truth_epoch` schema to include `proxy_set_version`.
3.  **Check**: On `ev_tick` startup, assert `Loaded_Proxy_Version == Truth_Epoch.proxy_version`. Raise `DiscontinuityError` if mismatch.
