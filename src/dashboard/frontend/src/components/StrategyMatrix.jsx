import React, { useEffect, useState } from 'react';
import { getStrategyEligibility } from '../services/api';
import './StrategyMatrix.css';

const FAMILY_DISPLAY_NAMES = {
    momentum: "Trend / Momentum",
    mean_reversion: "Mean Reversion",
    value: "Value",
    quality: "Quality / Defensive",
    carry: "Carry / Yield",
    volatility: "Volatility Strategies",
    spread: "Relative / Spread",
    stress: "Liquidity / Stress"
};

const FAMILY_ORDER = ["momentum", "mean_reversion", "value", "quality", "carry", "volatility", "spread", "stress"];

const StrategyMatrix = () => {
    const [data, setData] = useState(null);
    const [expandedFamily, setExpandedFamily] = useState(null);

    useEffect(() => {
        getStrategyEligibility().then(setData).catch(console.error);
    }, []);

    if (!data) return <div>Loading Strategy Universe...</div>;

    const families = data.families || {};
    const current_regime = data.current_regime || 'UNDEFINED';
    const current_factors = data.current_factors || {};

    const getFamilyStatus = (family) => {
        if (family.eligible_count > 0) return { icon: '🟢', label: 'ELIGIBLE', className: 'active' };

        const hasConditional = family.strategies.some(s => s.eligibility_status === 'conditional');
        if (hasConditional) return { icon: '⚠️', label: 'CONDITIONAL', className: 'conditional-family' };

        return { icon: '🔒', label: 'GATED', className: 'inactive' };
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'eligible': return <span className="status-badge eligible">✅ ELIGIBLE</span>;
            case 'conditional': return <span className="status-badge conditional">⚠️ CONDITIONAL</span>;
            default: return <span className="status-badge blocked">❌ BLOCKED</span>;
        }
    };

    const toggleFamily = (family) => {
        setExpandedFamily(expandedFamily === family ? null : family);
    };

    return (
        <div className="strategy-matrix narrative-focus">
            <div className="matrix-header">
                <h3 className="matrix-title">Strategy Universe Stories</h3>
                <div className="evolution-badge">Evolution Version: {data.evolution_version || 'v1'}</div>
            </div>

            <div className="family-story-grid">
                {FAMILY_ORDER.map(familyKey => {
                    const family = families[familyKey];
                    if (!family) return null;

                    const isExpanded = expandedFamily === familyKey;
                    const familyStatus = getFamilyStatus(family);

                    // Simple duration mock if not in data (should come from backend eventually)
                    const timeInState = "24 Ticks";

                    return (
                        <div key={familyKey} className={`story-block ${familyStatus.className}`}>
                            <div className="story-header" onClick={() => toggleFamily(familyKey)}>
                                <div className="story-main">
                                    <div className="story-name-row">
                                        <span className="story-icon">{familyStatus.icon}</span>
                                        <span className="story-family">{FAMILY_DISPLAY_NAMES[familyKey] || family.name}</span>
                                    </div>
                                    <span className="story-status-text">
                                        {familyStatus.label}
                                    </span>
                                </div>
                                <div className="story-meta">
                                    <span className="story-duration">{timeInState} in state</span>
                                </div>
                            </div>

                            <div className="story-narrative">
                                {family.explanation}
                            </div>

                            {isExpanded && (
                                <div className="story-details-panel">
                                    <h4 className="details-label">Individual Strategy Status</h4>
                                    <div className="strategy-list">
                                        {family.strategies.map((s, i) => (
                                            <div key={i} className={`strategy-item ${s.eligibility_status}`}>
                                                <div className="strategy-top">
                                                    <span className="s-name">{s.strategy}</span>
                                                    {getStatusBadge(s.eligibility_status)}
                                                </div>
                                                <div className="s-reason">{s.reason || "Structurally Gated"}</div>
                                                {s.activation_hint && (
                                                    <div className="s-hint">Requires: {s.activation_hint}</div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="story-footer" onClick={() => toggleFamily(familyKey)}>
                                {isExpanded ? 'Show Less' : 'View Strategies'}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default StrategyMatrix;
