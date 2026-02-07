import React, { useEffect, useState } from 'react';
import { getSystemStatus } from '../services/api';
import './SystemStatus.css';
import EpistemicHealthCheck from './EpistemicHealthCheck';
import './EpistemicHealthCheck.css';

const SystemStatus = ({ market }) => {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        getSystemStatus(market)
            .then(setData)
            .catch(err => {
                console.error(err);
                setError(err.message);
            });
    }, [market]);

    if (error) return <div className="status-banner error">Governance Error: {error}</div>;
    if (!data) return <div className="status-banner loading">Loading System Governance...</div>;

    const { gate, last_evaluation, trace } = data;
    const gateStatus = gate?.execution_gate || 'UNKNOWN';
    const isClosed = gateStatus === 'CLOSED' || gateStatus === 'UNKNOWN';
    const statusClass = `status-tag ${gateStatus.toLowerCase()}`;

    return (
        <div className="system-status_wrapper">
            <div className="system-status-banner">
                <div className="status-main">
                    <div className="gate-header">
                        <span className="role-id">A1.2</span>
                        <span className="label">EXECUTION GATE</span>
                    </div>
                    <span className={statusClass} title="Governed Permission to Execute">
                        {gateStatus}
                    </span>

                    <div className="gate-info">
                        {isClosed && (
                            <div className="disallowance-notice">
                                🛑 EXECUTION CATEGORICALLY DISALLOWED
                            </div>
                        )}
                        <div className="gate-reason">
                            <span className="reason-label">Constraint Reasons:</span>
                            <span className="reason-text">
                                {gate?.reasons?.join(' | ') || 'VERIFYING CONSTRAINTS...'}
                            </span>
                        </div>
                    </div>

                    <div className="trace-badge">
                        Trace: {trace?.gate_source} | Epoch: {gate?.truth_epoch || 'N/A'}
                    </div>
                </div>

                <div className="status-meta">
                    <div className="meta-item">
                        <div className="meta-header">
                            <span className="role-id">A1.3</span>
                            <span className="meta-label">LAST EVALUATION</span>
                        </div>
                        <span className="meta-value">{last_evaluation?.last_successful_evaluation || 'NONE'}</span>
                        <div className="trace-badge mini">
                            Source: {trace?.ev_source} | Epoch: {last_evaluation?.truth_epoch || 'N/A'}
                        </div>
                    </div>
                    <div className="meta-item">
                        <span className="meta-label">GOVERNANCE</span>
                        <span className="meta-value governance-clean">TE-2026-01-30 [FROZEN]</span>
                    </div>
                </div>
            </div>
            {isClosed && (
                <div className="alert-banner">
                    SYSTEM IS IN READ-ONLY MODE. NO TRADE PERMISSIONS GRANTED BY GOVERNANCE.
                </div>
            )}
        </div>
    );
};

export default SystemStatus;
