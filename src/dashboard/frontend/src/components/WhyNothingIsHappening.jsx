import React, { useEffect, useState } from 'react';
import { getSuppressionStatus } from '../services/api';
import './WhyNothingIsHappening.css';

const WhyNothingIsHappening = ({ market = 'US' }) => {
    const [payload, setPayload] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        getSuppressionStatus(market)
            .then((data) => {
                setPayload(data);
                setError(null);
            })
            .catch((err) => {
                console.error(err);
                setError(err.message);
                setPayload(null);
            });
    }, [market]);

    if (error) {
        return (
            <div className="why-panel">
                <h3 className="why-title">Why Nothing Is Happening [{market}]</h3>
                <div className="suppression-header blocked">ACTION BLOCKED DUE TO: SUPPRESSION STATE UNAVAILABLE</div>
                <div className="reason-card">
                    <div className="reason-condition">Unable to load suppression registry: {error}</div>
                </div>
            </div>
        );
    }

    if (!payload?.suppression) {
        return (
            <div className="why-panel">
                <h3 className="why-title">Why Nothing Is Happening [{market}]</h3>
                <div className="suppression-header blocked">ACTION BLOCKED DUE TO: NO SUPPRESSION DATA</div>
            </div>
        );
    }

    const suppression = payload.suppression || {};
    const primary = suppression.primary_reason || {};
    const secondary = suppression.secondary_reasons || [];
    const state = suppression.suppression_state || 'NONE';
    const isBlocked = state !== 'NONE';

    return (
        <div className="why-panel">
            <h3 className="why-title">Why Nothing Is Happening [{market}]</h3>
            <div className={`suppression-header ${isBlocked ? 'blocked' : 'clear'}`}>
                {isBlocked ? `ACTION BLOCKED DUE TO: ${state}` : 'NO ACTIVE SUPPRESSION STATE'}
            </div>

            <div className="blocker-checklist">
                <div className="reason-card">
                    <div className="reason-label">Suppression State</div>
                    <div className="reason-value">{state}</div>
                </div>

                <div className="reason-card">
                    <div className="reason-label">Primary Reason</div>
                    <div className="reason-value">{primary.reason_id || 'NONE'}</div>
                    <div className="reason-condition">{primary.blocking_condition || 'No active blocker condition.'}</div>
                </div>

                <div className="reason-card">
                    <div className="reason-label">Since Timestamp</div>
                    <div className="reason-value">{suppression.since_timestamp || primary.since_timestamp || 'N/A'}</div>
                </div>

                <div className="reason-card">
                    <div className="reason-label">Clearing Condition</div>
                    <div className="reason-condition">{primary.clearing_condition || 'No clearing condition required.'}</div>
                </div>

                {secondary.length > 0 && (
                    <div className="reason-card">
                        <div className="reason-label">Secondary Reasons</div>
                        {secondary.map((item) => (
                            <div key={item.reason_id} className="secondary-row">
                                <span className="secondary-id">{item.reason_id}</span>
                                <span className="secondary-text">{item.blocking_condition}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="why-footer">
                Truth Epoch: {suppression.truth_epoch || 'TE-2026-01-30'} | Execution remains disabled | Capital remains disabled
            </div>
        </div>
    );
};

export default WhyNothingIsHappening;

