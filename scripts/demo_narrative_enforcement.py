"""
Demo script: Narrative Regime Enforcement
"""
from traderfund.regime.narrative_adapter import (
    apply_regime_to_narrative, 
    NarrativeSignal,
    get_current_us_market_regime
)
import json

# Get current regime
regime = get_current_us_market_regime()
print('=' * 60)
print('CURRENT US MARKET REGIME')
print('=' * 60)
print(f'Regime    : {regime.regime}')
print(f'Bias      : {regime.bias}')
print(f'Confidence: {regime.confidence}')
print(f'Lifecycle : {regime.lifecycle}')
print(f'Posture   : {regime.posture}')
print(f'Weight    : {regime.narrative_weight}x')
print()

# Test various narrative signals
test_signals = [
    ('AAPL', 1.0, 'Apple momentum signal'),
    ('MSFT', 0.8, 'Microsoft earnings narrative'),
    ('TSLA', 0.9, 'Tesla volatility play'),
    ('NVDA', 0.7, 'NVDA AI narrative'),
    ('SPY', 1.0, 'Broad market long'),
]

print('=' * 60)
print('NARRATIVE ENFORCEMENT OUTPUT')
print('=' * 60)
print(f"{'Symbol':<8} {'Original':<10} {'Final':<10} {'Factor':<8} Reason")
print('-' * 60)

for symbol, weight, summary in test_signals:
    sig = NarrativeSignal(
        symbol=symbol,
        weight=weight,
        confidence=0.9,
        narrative_id=f'{symbol.lower()}-001',
        summary=summary
    )
    result = apply_regime_to_narrative(sig)
    reason_short = result.enforcement_reason[:40]
    print(f'{symbol:<8} {result.original_weight:<10.2f} {result.final_weight:<10.2f} {result.adjustment_factor:<8.2f} {reason_short}')

print()
print('=' * 60)
print('TELEMETRY LOG (last 5 entries)')
print('=' * 60)
try:
    with open('data/regime_narrative_telemetry.jsonl', 'r') as f:
        lines = f.readlines()[-5:]
        for line in lines:
            data = json.loads(line)
            reason = data['enforcement_reason'][:35]
            print(f"{data['symbol']}: {data['original_weight']} -> {data['final_weight']} | {reason}")
except Exception as e:
    print(f'Error: {e}')
