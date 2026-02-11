import React, { useEffect, useState } from 'react';
import { getIntelligenceSnapshot } from '../services/api';
import { useInspection } from '../context/InspectionContext';
import './IntelligencePanel.css';
import PolicyStateCard from './PolicyStateCard';
import FragilityStateCard from './FragilityStateCard';

const IntelligencePanel = ({ market }) => {
    // Market is now passed as prop
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const { isInspectionMode } = useInspection();

    useEffect(() => {
        if (!isInspectionMode) {
            setLoading(true);
            getIntelligenceSnapshot(market)
                .then(res => {
                    setData(res);
                    setLoading(false);
                })
                .catch(err => {
                    console.error(err);
                    setLoading(false);
                });
        }
    }, [market, isInspectionMode]);

    const SignalCard = ({ signal }) => (
        <div className={`signal-card ${signal.overlay?.status?.toLowerCase()}`}>
            <div className="sig-header">
                <span className="sig-symbol">{signal.symbol}</span>
                <span className="sig-type">{signal.type.replace('_', ' ')}</span>
            </div>
            {signal.explanation && (
                <div className="sig-explanation">
                    <div className="exp-item"><strong>What:</strong> {signal.explanation.what}</div>
                    <div className="exp-item"><strong>Why:</strong> {signal.explanation.why}</div>
                    <div className="exp-item not"><strong>Not:</strong> {signal.explanation.not}</div>
                </div>
            )}
            <div className="sig-reason-legacy">{signal.reason}</div>
            {signal.overlay && (
                <div className="sig-overlay">
                    <span className="overlay-badge">{signal.overlay.status}</span>
                    <span className="overlay-reason">{signal.overlay.reason}</span>
                </div>
            )}
        </div>
    );

    // If loading or error, we still want to show Policy if possible, but structure prevents it easily.
    // For now, let's render layout first then content logic.

    // Fallback data if null
    const signals = data ? data.signals : [];
    const timestamp = data ? data.timestamp : null;

    const attentionSignals = signals.filter(s => s.overlay?.status !== 'BLOCKED');
    const blockedSignals = signals.filter(s => s.overlay?.status === 'BLOCKED');

    return (
        <div className={`intelligence-panel ${isInspectionMode ? 'inspection' : ''}`}>
            <div className="intel-header">
                <div className="intel-title-block">
                    <h3>👁️ Intelligence Layer</h3>
                    <div className="intel-subtitle">Attention Only • No Execution</div>
                </div>
            </div>

            {/* GOVERNANCE: Policy State Card */}
            <PolicyStateCard market={market} />

            {/* SYSTEMIC: Fragility & Stress Card */}
            <FragilityStateCard market={market} />

            <div className="intel-content">
                {isInspectionMode ? (
                    <div className="inspection-blocker">
                        <h4>SIGNALS UNAVAILABLE IN INSPECTION MODE</h4>
                        <p>Simulated signal generation is not supported in this view. Refer to Policy and Fragility cards for stress verdicts derived from Phase 3 Audit Artifacts.</p>
                    </div>
                ) : (
                    <>
                        <div className="intel-column">
                            <h4>Attention ({attentionSignals.length})</h4>
                            {loading ? <div>Loading signals...</div> : (
                                <div className="signal-list">
                                    {attentionSignals.length === 0 ? <div className="empty-msg">No active signals</div> :
                                        attentionSignals.map((s, i) => <SignalCard key={i} signal={s} />)}
                                </div>
                            )}
                        </div>

                        <div className="intel-column blocked">
                            <h4>Blocked by Research ({blockedSignals.length})</h4>
                            {loading ? <div>Loading...</div> : (
                                <div className="signal-list">
                                    {blockedSignals.length === 0 ? <div className="empty-msg">None blocked</div> :
                                        blockedSignals.map((s, i) => <SignalCard key={i} signal={s} />)}
                                </div>
                            )}
                        </div>
                    </>
                )}
            </div>

            <div className="intel-footer">
                {timestamp && `Timestamp: ${new Date(timestamp).toLocaleString()}`}
            </div>
        </div>
    );
};

export default IntelligencePanel;
