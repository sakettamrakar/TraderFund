import React, { useEffect, useState } from 'react';
import { getMarketSnapshot } from '../services/api';
import { useInspection } from '../context/InspectionContext';
import './MarketSnapshot.css';

const MarketSnapshot = ({ market }) => {
    const [snapshot, setSnapshot] = useState(null);
    const [showFactorDetail, setShowFactorDetail] = useState(false);
    const { isInspectionMode } = useInspection();

    useEffect(() => {
        if (!isInspectionMode) {
            getMarketSnapshot(market).then(setSnapshot).catch(console.error);
        }
    }, [market, isInspectionMode]);

    if (isInspectionMode) {
        return (
            <div className="market-snapshot inspection-blocked">
                <div className="snapshot-header">
                    <h3>Market Structure Snapshot</h3>
                    <div className="weather-icon">🚫</div>
                </div>
                <div className="inspection-msg">
                    MARKET DATA UNAVAILABLE IN SCENARIO VISUALIZATION. <br />
                    LIVE PRICE/VOLUMETRICS ARE SUPPRESSED.
                </div>
            </div>
        );
    }

    if (!snapshot) return <div>Loading...</div>;

    const metrics = [
        { label: 'REGIME', value: snapshot.Regime || 'UNKNOWN' },
        { label: 'LIQUIDITY', value: snapshot.Liquidity || 'UNKNOWN' },
        { label: 'MOMENTUM', value: snapshot.Momentum || 'UNKNOWN' },
        { label: 'EXPANSION', value: snapshot.Expansion || 'NONE' },
        { label: 'DISPERSION', value: snapshot.Dispersion || 'NONE' },
    ];
    const regimeDegraded = snapshot.RegimeDegraded || snapshot.CanonicalState !== 'CANONICAL_COMPLETE';
    const missingRoles = snapshot.MissingRoles || [];
    const staleRoles = snapshot.StaleRoles || [];

    // T-DASH-04: Market Proxy Sets (Explicit Data Declaration)
    const PROXY_MAP = {
        'US': { name: 'S&P 500', source: 'SPY.csv (Yahoo Finance)' },
        'INDIA': { name: 'NIFTY 50 (Proxy)', source: 'NIFTY50.csv (Yahoo Finance)' }
    };
    const activeProxy = PROXY_MAP[market] || { name: 'Unknown', source: 'Unknown' };

    return (
        <div className="market-snapshot">
            <div className="proxy-header">
                <span className="proxy-label">OBSERVING PROXY:</span>
                <span className="proxy-value">{activeProxy.name}</span>
                <span className="proxy-source" title={`Data Source: ${activeProxy.source}`}>[{activeProxy.source}]</span>
            </div>
            {regimeDegraded && (
                <div className="partiality-banner">
                    <div className="partiality-title">REGIME: UNKNOWN (PARTIAL DATA)</div>
                    <div className="partiality-row">Canonical State: {snapshot.CanonicalState || 'UNKNOWN'}</div>
                    <div className="partiality-row">Reason: {snapshot.RegimeReason || 'Partial canonical inputs'}</div>
                    <div className="partiality-row">
                        Missing Roles: {missingRoles.length ? missingRoles.join(', ') : 'NONE'} | Stale Roles: {staleRoles.length ? staleRoles.join(', ') : 'NONE'}
                    </div>
                </div>
            )}
            {snapshot.Alerts && snapshot.Alerts.length > 0 && (
                <div className="alerts-section">
                    <h4>Recent Transitions</h4>
                    {snapshot.Alerts.map((alert, i) => (
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
                    const durationData = snapshot.Durations ? snapshot.Durations[m.label] : null;
                    return (
                        <div key={m.label} className="metric-card">
                            <span className="metric-label">{m.label}</span>
                            <span className="metric-value">{m.value}</span>
                            {durationData && (
                                <span className="metric-duration" title={`Since ${durationData.since}`}>
                                    In State: {durationData.duration}
                                </span>
                            )}
                            {/* T-DASH-05: Transparency Tooltip */}
                            <div className="metric-tooltip">
                                Driven by: {
                                    m.label === 'MOMENTUM' ? 'Price SMA50 x SMA200' :
                                        m.label === 'LIQUIDITY' ? 'Avg Daily Volume (20d)' :
                                            m.label === 'EXPANSION' ? 'ATR Breakout > 1.5σ' :
                                                'Regime Classification Model'
                                }
                            </div>
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
                            <span className="factor-state">{snapshot?.Details?.Momentum || 'Flat'}</span>
                            <span className="factor-desc">Speed of the trend. Flat = No new power.</span>
                        </div>
                        <div className="factor-item">
                            <span className="factor-name">Breadth</span>
                            <span className="factor-state">{'Narrow'}</span>
                            <span className="factor-desc">Market participation. Narrow = Few stocks leading.</span>
                        </div>
                        <div className="factor-item">
                            <span className="factor-name">Expansion</span>
                            <span className="factor-state">{snapshot?.Expansion || 'None'}</span>
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
