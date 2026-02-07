import React, { useEffect, useState } from 'react';
import { getCapitalReadiness } from '../services/api';
import './CapitalReadinessPanel.css';

const CapitalReadinessPanel = ({ market }) => {
    const [readiness, setReadiness] = useState(null);

    useEffect(() => {
        getCapitalReadiness(market).then(setReadiness).catch(console.error);
    }, [market]);

    if (!readiness) return <div className="loading-cap">Loading Capital Logic...</div>;

    const { status, drawdown_state, kill_switch, allocations, meta } = readiness;
    const totalCapital = meta?.total_capital || 100;

    // Hardcoded ceilings for visualization based on docs/capital/capital_buckets.md
    const CEILINGS = {
        "momentum": 0.25,
        "mean_reversion": 0.0,
        "value": 0.35,
        "quality": 0.35,
        "carry": 0.15,
        "volatility": 0.25,
        "spread": 0.15,
        "stress": 0.10
    };

    return (
        <div className="capital-panel">
            <h3 className="cap-title">Capital Readiness ({market}) (Paper Only)</h3>

            <div className="cap-status-row">
                <div className={`status - badge ${status === 'READY' ? 'ready' : 'not-ready'} `}>
                    {status === 'READY' ? '✅ READY' : '🛑 NOT READY'}
                </div>
                <div className={`status - badge ${drawdown_state === 'NORMAL' ? 'normal' : 'warning'} `}>
                    DD: {drawdown_state}
                </div>
                <div className={`status - badge ${kill_switch?.global === 'DISARMED' ? 'normal' : 'critical'} `}>
                    KS: {kill_switch?.global || 'UNKNOWN'}
                </div>
            </div>

            <div className="bucket-grid">
                {Object.entries(CEILINGS).map(([family, ceilingPct]) => {
                    const alloc = allocations?.[family] || 0;
                    const allocPct = (alloc / totalCapital);
                    const ceilingVal = ceilingPct * 100;

                    return (
                        <div key={family} className="bucket-item">
                            <div className="bucket-header">
                                <span className="bucket-name">{family.replace('_', ' ').split(' ').map(s => s.charAt(0).toUpperCase() + s.substring(1)).join(' ')}</span>
                                <span className="bucket-val">{Math.round(allocPct * 100)}% / {ceilingVal}%</span>
                            </div>
                            <div className="bucket-bar-bg">
                                <div
                                    className="bucket-bar-fill"
                                    style={{ width: `${(allocPct / ceilingPct) * 100}% ` }}
                                ></div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="cap-footer">
                * Allocations are symbolic. No real capital is deployed.
            </div>
        </div>
    );
};

export default CapitalReadinessPanel;
