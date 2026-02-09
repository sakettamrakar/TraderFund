import React, { useEffect, useState } from 'react';
import { getMacroContext } from '../services/api';
import { useInspection } from '../context/InspectionContext';
import './MacroContextPanel.css';

const MacroContextPanel = ({ market }) => {
    const [context, setContext] = useState(null);
    const { isInspectionMode } = useInspection();

    useEffect(() => {
        if (!isInspectionMode) {
            getMacroContext(market).then(setContext).catch(console.error);
        }
    }, [market, isInspectionMode]);

    if (isInspectionMode) {
        return (
            <div className="macro-weather-panel inspection-blocked">
                <div className="macro-header">
                    <div className="weather-icon">🚫</div>
                    <div className="macro-title-block">
                        <h3>Macro Context Layer</h3>
                        <div className="macro-timestamp">INSPECTION MODE</div>
                    </div>
                </div>
                <div className="inspection-msg">
                    MACRO DATA UNAVAILABLE IN SCENARIO VISUALIZATION. <br />
                    REFER TO POLICY STATE FOR STRESS IMPACTS.
                </div>
            </div>
        );
    }

    if (!context) return <div className="loading-macro">Loading Macro Weather...</div>;

    // Optional: handle error state if context is empty
    if (context.error) return <div className="macro-error">Macro Data Unavailable</div>;

    const { monetary, liquidity, growth_inflation, risk, summary_narrative, timestamp } = context;

    // Helper to render a macro cell
    const MacroCell = ({ label, value, stateClass, scope }) => (
        <div className={`macro-cell ${stateClass}`}>
            <div className="macro-label">
                {scope && <span className="macro-scope-tag">[{scope}]</span>}
                {label}
            </div>
            <div className="macro-value">{value}</div>
        </div>
    );

    // Determine scope tags based on active market
    const localScope = market === 'US' ? 'US' : 'IN';
    const globalScope = 'GL';

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
                    <MacroCell label="Policy" value={monetary.policy_stance} stateClass={monetary.policy_stance.toLowerCase()} scope={localScope} />
                    <MacroCell label="Rates" value={monetary.rate_level} stateClass="neutral" scope={localScope} />
                    <MacroCell label="Curve" value={monetary.curve_shape} stateClass={monetary.curve_shape === 'INVERTED' ? 'negative' : 'neutral'} scope={localScope} />
                </div>

                {/* Liquidity Column */}
                <div className="macro-col">
                    <h4>Liquidity</h4>
                    <MacroCell label="Impulse" value={liquidity.impulse} stateClass={liquidity.impulse === 'CONTRACTING' ? 'negative' : 'neutral'} scope={globalScope} />
                    <MacroCell label="Spreads" value={liquidity.credit_spreads} stateClass={liquidity.credit_spreads === 'WIDE' ? 'negative' : 'positive'} scope={localScope} />
                </div>

                {/* Risk Column */}
                <div className="macro-col">
                    <h4>Risk Sentiment</h4>
                    <MacroCell label="Appetite" value={risk.appetite} stateClass={risk.appetite === 'RISK-OFF' ? 'negative' : 'positive'} scope={globalScope} />
                    <MacroCell label="Volatility" value={risk.volatility} stateClass={risk.volatility === 'ELEVATED' ? 'negative' : 'positive'} scope={localScope} />
                </div>
            </div>

            <div className="macro-footer">
                * Explanatory Context Only. Does not execute.
            </div>
        </div>
    );
};

export default MacroContextPanel;
