import React, { useEffect, useState } from 'react';
import { getCapitalHistory } from '../services/api';
import './CapitalStoryPanel.css';

const CapitalStoryPanel = ({ market }) => {
    const [history, setHistory] = useState(null);

    useEffect(() => {
        getCapitalHistory(market).then(setHistory).catch(console.error);
    }, [market]);

    if (!history) return <div className="loading-story">Loading Narrative History...</div>;

    const { timeline, current_posture } = history;

    // Invariants Checklist (Static for now, could be dynamic)
    const INVARIANTS = [
        { label: "Execution Authorization", passed: false, reason: "No execution paths enabled." },
        { label: "Volatility Expansion", passed: false, reason: "Market in NEUTRAL/COMPRESSED state." },
        { label: "Dispersion Breakout", passed: false, reason: "No significant dispersion detected." },
        { label: "Strategy Confirmation", passed: false, reason: "Evolution rules not satisfied." }
    ];

    return (
        <div className="capital-story-panel">
            <div className="story-top-summary">
                <div className="summary-icon">📖</div>
                <div className="summary-text-block">
                    <h3 className="story-title">Capital Narrative</h3>
                    <div className="story-subtitle">
                        Checking <strong>{timeline.length}</strong> historical frames. Current Posture: <span className={`posture-tag ${current_posture.toLowerCase()}`}>{current_posture}</span>
                    </div>
                </div>
            </div>

            <div className="why-checklist">
                <h4 className="section-header">Why Capital Has Not Moved</h4>
                {INVARIANTS.map((inv, i) => (
                    <div key={i} className="checklist-item">
                        <span className="check-icon">{inv.passed ? '✅' : '❌'}</span>
                        <div className="check-detail">
                            <div className="check-label">{inv.label}</div>
                            <div className="check-reason">{inv.reason}</div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="counterfactual-box">
                <div className="cf-title">Counterfactual Reality</div>
                <div className="cf-text">
                    Even if momentum strategies were eligible, capital would still be constrained by family ceilings (Momentum ≤ 25%) and portfolio risk envelopes. No single strategy could exceed its symbolic limit. <strong>Capital remains idle by design.</strong>
                </div>
            </div>

            <div className="timeline-section">
                <h4 className="section-header">Recent State History</h4>
                <div className="timeline-list">
                    {timeline.length === 0 ? (
                        <div className="empty-history">No history recorded yet. Awaiting first tick.</div>
                    ) : (
                        timeline.map((entry, idx) => (
                            <div key={idx} className="timeline-row">
                                <div className="t-time">{new Date(entry.timestamp).toLocaleTimeString()}</div>
                                <div className={`t-state ${entry.state.toLowerCase()}`}>{entry.state}</div>
                                <div className="t-reason">{entry.reason}</div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default CapitalStoryPanel;
