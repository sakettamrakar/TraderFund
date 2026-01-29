import React, { useEffect, useState } from 'react';
import { getMacroContext } from '../services/api';
import './MacroContextPanel.css';

const MacroContextPanel = ({ market = "US" }) => {
    const [context, setContext] = useState(null);

    useEffect(() => {
        getMacroContext(market).then(setContext).catch(console.error);
    }, [market]);

    if (!context) return <div className="loading-macro">Loading Macro Weather...</div>;

    // Optional: handle error state if context is empty
    if (context.error) return <div className="macro-error">Macro Data Unavailable</div>;

    const { monetary, liquidity, growth_inflation, risk, summary_narrative, timestamp } = context;

    // Helper to render a macro cell
    const MacroCell = ({ label, value, stateClass }) => (
        <div className={`macro-cell ${stateClass}`}>
            <div className="macro-label">{label}</div>
            <div className="macro-value">{value}</div>
        </div>
    );

    return (
        <div className="macro-weather-panel">
            <div className="macro-header">
                <div className="weather-icon">🌤️</div>
                <div className="macro-title-block">
                    <h3>Macro Context Layer</h3>
                    <div className="macro-timestamp">Snapshot: {new Date(timestamp).toLocaleDateString()}</div>
                </div>
            </div>

            <div className="macro-narrative-box">
                "{summary_narrative}"
            </div>

            <div className="macro-grid">
                {/* Monetary Column */}
                <div className="macro-col">
                    <h4>Monetary</h4>
                    <MacroCell label="Policy" value={monetary.policy_stance} stateClass={monetary.policy_stance.toLowerCase()} />
                    <MacroCell label="Rates" value={monetary.rate_level} stateClass="neutral" />
                    <MacroCell label="Curve" value={monetary.curve_shape} stateClass={monetary.curve_shape === 'INVERTED' ? 'negative' : 'neutral'} />
                </div>

                {/* Liquidity Column */}
                <div className="macro-col">
                    <h4>Liquidity</h4>
                    <MacroCell label="Impulse" value={liquidity.impulse} stateClass={liquidity.impulse === 'CONTRACTING' ? 'negative' : 'neutral'} />
                    <MacroCell label="Spreads" value={liquidity.credit_spreads} stateClass={liquidity.credit_spreads === 'WIDE' ? 'negative' : 'positive'} />
                </div>

                {/* Risk Column */}
                <div className="macro-col">
                    <h4>Risk Sentiment</h4>
                    <MacroCell label="Appetite" value={risk.appetite} stateClass={risk.appetite === 'RISK-OFF' ? 'negative' : 'positive'} />
                    <MacroCell label="Volatility" value={risk.volatility} stateClass={risk.volatility === 'ELEVATED' ? 'negative' : 'positive'} />
                </div>
            </div>

            <div className="macro-footer">
                * Explanatory Context Only. Does not execute.
            </div>
        </div>
    );
};

export default MacroContextPanel;
