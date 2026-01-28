import React, { useEffect, useState } from 'react';
import { getMarketSnapshot } from '../services/api';
import './MarketSnapshot.css';

const MarketSnapshot = () => {
    const [snap, setSnap] = useState(null);
    const [showFactorDetail, setShowFactorDetail] = useState(false);

    useEffect(() => {
        getMarketSnapshot().then(setSnap).catch(console.error);
    }, []);

    if (!snap) return <div>Loading...</div>;

    const metrics = [
        { label: 'REGIME', value: snap.regime?.state || 'UNKNOWN' },
        { label: 'LIQUIDITY', value: snap.liquidity?.state || 'UNKNOWN', sub: snap.liquidity?.note },
        { label: 'MOMENTUM', value: snap.momentum?.state || 'UNKNOWN' },
        { label: 'EXPANSION', value: snap.expansion?.state || 'NONE' },
        { label: 'DISPERSION', value: snap.dispersion?.state || 'NONE' },
    ];

    return (
        <div className="market-snapshot">
            {snap.Alerts && snap.Alerts.length > 0 && (
                <div className="alerts-section">
                    <h4>Recent Transitions</h4>
                    {snap.Alerts.map((alert, i) => (
                        <div key={i} className="audit-alert">
                            <span className="alert-icon">⚡</span>
                            <span className="alert-text">{alert}</span>
                        </div>
                    ))}
                </div>
            )}

            <div className="snapshot-header">
                <h3>Market Structure Snapshot</h3>
                <button
                    className="details-toggle"
                    onClick={() => setShowFactorDetail(!showFactorDetail)}
                >
                    {showFactorDetail ? 'Hide Factors' : 'View Detail'}
                </button>
            </div>

            <div className="snapshot-grid">
                {metrics.map((m) => {
                    // Extract duration for this metric if available
                    const durationData = snap.Durations ? snap.Durations[m.label] : null;
                    return (
                        <div key={m.label} className="metric-card">
                            <span className="metric-label">{m.label}</span>
                            <span className="metric-value">{m.value}</span>
                            {durationData && (
                                <span className="metric-duration" title={`Since ${durationData.since}`}>
                                    In State: {durationData.duration}
                                </span>
                            )}
                            {m.sub && <span className="metric-sub">{m.sub}</span>}
                        </div>
                    );
                })}
            </div>

            {showFactorDetail && (
                <div className="factor-breakdown-panel">
                    <h4>Momentum Factor Breakdown (Diagnostic)</h4>
                    <div className="factor-list">
                        <div className="factor-item">
                            <span className="factor-name">Acceleration</span>
                            <span className="factor-state">{snap?.momentum?.acceleration || 'Flat'}</span>
                            <span className="factor-desc">Speed of the trend. Flat = No new power.</span>
                        </div>
                        <div className="factor-item">
                            <span className="factor-name">Breadth</span>
                            <span className="factor-state">{snap?.momentum?.breadth || 'Narrow'}</span>
                            <span className="factor-desc">Market participation. Narrow = Few stocks leading.</span>
                        </div>
                        <div className="factor-item">
                            <span className="factor-name">Expansion</span>
                            <span className="factor-state">{snap?.expansion?.state || 'None'}</span>
                            <span className="factor-desc">Volatility opening. None = Market is contracting.</span>
                        </div>
                    </div>
                    <div className="panel-footer">
                        * These indicators explain why Momentum strategies may remain "Gated" even if a trend exists.
                    </div>
                </div>
            )}
        </div>
    );
};

export default MarketSnapshot;
