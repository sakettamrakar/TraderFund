import React, { useEffect, useState } from 'react';
import { getSystemStatus } from '../services/api';
import { useInspection } from '../context/InspectionContext';
import './SystemStatus.css';
import './SystemStatusInspection.css';
import EpistemicHealthCheck from './EpistemicHealthCheck';
import './EpistemicHealthCheck.css';

const SystemStatus = ({ market }) => {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const { isInspectionMode, toggleInspection, scenarios, selectScenario, selectedScenarioId, activeScenario } = useInspection();

    useEffect(() => {
        if (!isInspectionMode) {
            getSystemStatus(market)
                .then(setData)
                .catch(err => {
                    console.error(err);
                    setError(err.message);
                });
        }
    }, [market, isInspectionMode]);

    // Derived State
    let gateStatus = 'UNKNOWN';
    let isClosed = true;
    let reasons = [];
    let traceData = {};
    let lastEval = 'NONE';

    if (isInspectionMode) {
        gateStatus = 'CLOSED (SIMULATION)';
        isClosed = true;
        reasons = ['INSPECTION MODE ACTIVE', activeScenario ? activeScenario.condition_desc : 'SELECT SCENARIO'];
        traceData = { gate_source: 'Scenario Report', ev_source: 'N/A' };
        lastEval = 'SIMULATED';
    } else if (data) {
        const { gate, last_evaluation, trace } = data;
        gateStatus = gate?.execution_gate || 'UNKNOWN';
        isClosed = gateStatus === 'CLOSED' || gateStatus === 'UNKNOWN';
        reasons = gate?.reasons || [];
        traceData = trace;
        lastEval = last_evaluation?.last_successful_evaluation || 'NONE';
    }

    const statusClass = `status-tag ${gateStatus.toLowerCase().split(' ')[0]}`; // Handle 'CLOSED (SIM)'

    if (error && !isInspectionMode) return <div className="status-banner error">Governance Error: {error}</div>;
    if (!data && !isInspectionMode) return <div className="status-banner loading">Loading System Governance...</div>;

    return (
        <div className={`system-status_wrapper ${isInspectionMode ? 'inspection-root' : ''}`}>

            {/* INSPECTION CONTROLS */}
            <div className="inspection-controls">
                <button
                    className={`inspection-toggle ${isInspectionMode ? 'active' : ''}`}
                    onClick={toggleInspection}
                >
                    {isInspectionMode ? 'EXIT INSPECTION' : 'ENTER INSPECTION MODE'}
                </button>

                {isInspectionMode && (
                    <div className="scenario-selector">
                        <span className="scen-label">SELECT SCENARIO:</span>
                        {scenarios.map(s => (
                            <button
                                key={s.id}
                                className={`scen-btn ${selectedScenarioId === s.id ? 'active' : ''}`}
                                onClick={() => selectScenario(s.id)}
                            >
                                {s.id}: {s.name}
                            </button>
                        ))}
                    </div>
                )}
            </div>

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
                                {isInspectionMode ? '🛑 SIMULATION: EXECUTION DISABLED' : '🛑 EXECUTION CATEGORICALLY DISALLOWED'}
                            </div>
                        )}
                        <div className="gate-reason">
                            <span className="reason-label">Constraint Reasons:</span>
                            <span className="reason-text">
                                {reasons.join(' | ') || 'VERIFYING CONSTRAINTS...'}
                            </span>
                        </div>
                    </div>

                    <div className="trace-badge">
                        Trace: {traceData?.gate_source} | Epoch: {isInspectionMode ? 'INSPECTION' : (data?.gate?.truth_epoch || 'N/A')}
                    </div>
                </div>

                <div className="status-meta">
                    <div className="meta-item">
                        <div className="meta-header">
                            <span className="role-id">A1.3</span>
                            <span className="meta-label">LAST EVALUATION</span>
                        </div>
                        <span className="meta-value">{lastEval}</span>
                        <div className="trace-badge mini">
                            Source: {traceData?.ev_source}
                        </div>
                    </div>
                    <div className="meta-item">
                        <span className="meta-label">GOVERNANCE</span>
                        <span className="meta-value governance-clean">TE-2026-01-30 [FROZEN]</span>
                    </div>
                </div>
            </div>
            {isClosed && !isInspectionMode && (
                <div className="alert-banner">
                    SYSTEM IS IN READ-ONLY MODE. NO TRADE PERMISSIONS GRANTED BY GOVERNANCE.
                </div>
            )}
            {isInspectionMode && (
                <div className="alert-banner inspection">
                    ⚠️ INSPECTION MODE ACTIVE — DISPLAYING STATIC STRESS SCENARIOS — NOT LIVE TRUTH
                </div>
            )}
        </div>
    );
};

export default SystemStatus;
