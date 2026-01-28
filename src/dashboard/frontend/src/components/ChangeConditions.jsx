import React from 'react';
import './ChangeConditions.css';

const ChangeConditions = () => {
    return (
        <div className="change-conditions">
            <h3>What Conditions Would Enable New Trades?</h3>
            <div className="layman-intro">
                The system exercises restraint when the market lacks structure.
                Below are the conditions that would open the safety gates.
            </div>

            <div className="condition-box">
                <h4>Momentum Strategies (Trend Following)</h4>
                <p className="causal-reasoning">
                    We wait for a "Market Wake-up". Momentum needs a move that is broad and powerful to be safe.
                </p>
                <ul>
                    <li><strong>Market Expansion</strong>: Volatility must "open up" (move from <code>NONE</code> to <code>EARLY</code>). This creates room for price to move.</li>
                    <li><strong>Factor Dispersion</strong>: Stock prices must spread out (<code>BREAKOUT</code>). This signals that a new trend is being established.</li>
                    <li><strong>Confirmation</strong>: The trend must show it can sustain itself across multiple time windows.</li>
                </ul>
            </div>

            <div className="condition-box">
                <h4>Value Strategies (Buy the Dip)</h4>
                <p className="causal-reasoning">
                    We wait for "Extreme Mispricing". We only act when the market has pushed prices far from their fair value.
                </p>
                <ul>
                    <li><strong>Price Spread</strong>: Must be <code>WIDE</code> or <code>EXTREME</code>. This gives us a "safety margin".</li>
                    <li><strong>Liquidity</strong>: The market must remain orderly. We avoid "Crashes" where selling becomes indiscriminate and dangerous.</li>
                </ul>
            </div>

            <div className="note-footer">
                * These explanations are purely informational and describe the system's encoded trading philosophy.
            </div>
        </div>
    );
};

export default ChangeConditions;
