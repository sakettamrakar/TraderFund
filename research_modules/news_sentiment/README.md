# News & Sentiment Analysis Module (Module D)

## RESEARCH-ONLY

> ⚠️ **WARNING**: This module is strictly for research purposes.
> Sentiment must NEVER override price/volume signals.

---

## Purpose

This module answers:

> "What narratives and information flows exist around a symbol?"

It provides **observations** about news sentiment. It does NOT make trade decisions.

---

## What This Module MEASURES

✅ **Sentiment Polarity:** -1.0 (negative) to +1.0 (positive)
✅ **Confidence Level:** How much sentiment-bearing text was found
✅ **Event Tags:** Earnings, regulation, macro, management, etc.
✅ **Dominant Topics:** Most frequent content words

---

## Why Sentiment is Noisy and Lagging

| Issue | Reality |
|-------|---------|
| Delayed | News often arrives after price moves |
| Biased | Sources have editorial slant |
| Contradictory | Multiple sources say opposite things |
| Priced In | Market may have already reacted |

---

## Common Cognitive Traps

1. **Confirmation Bias:** Seeking news that confirms your position
2. **Hindsight Narrative:** Fitting news to explain past moves
3. **Availability Heuristic:** Overweighting recent/dramatic news
4. **Authority Bias:** Trusting "experts" without verification

**Rule:** Sentiment is context, not a signal.

---

## Usage

```bash
python -m research_modules.news_sentiment.cli \
    --symbol ITC \
    --news-file news_data.json \
    --research-mode
```

---

## See Also

- [PHASE_LOCK.md](./PHASE_LOCK.md)
- [docs/governance/RESEARCH_MODULE_GOVERNANCE.md](../../docs/governance/RESEARCH_MODULE_GOVERNANCE.md)
