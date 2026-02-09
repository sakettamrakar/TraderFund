import React, { useState, useEffect } from 'react';
import { getMarketPolicy } from '../services/api';
import { useInspection } from '../context/InspectionContext';
import './PolicyStateCard.css';

const PolicyStateCard = ({ market }) => {
    const [policyData, setPolicyData] = useState(null);
    const [error, setError] = useState(null);
    const { isInspectionMode, activeScenario, meta } = useInspection();

    useEffect(() => {
        if (!isInspectionMode) {
            getMarketPolicy(market)
                .then(data => {
                    setPolicyData(data.policy);
                    setError(null);
                })
                .catch(err => {
                    console.error(err);
                    setError(err.message);
                    setPolicyData(null);
                });
        }
    }, [market, isInspectionMode]);

    let finalPolicyData = isInspectionMode ? null : policyData;
    let isSimulated = isInspectionMode;

    if (isInspectionMode) {
        if (activeScenario) {
            const outcomes = activeScenario.markets?.[market]?.outcomes;
            if (outcomes) {
                // Synthesize Policy Object from Audit Report structure
                const pState = outcomes.policy_state || 'RESTRICTED';
                const blocked = outcomes.blocked_actions || (outcomes.constraints ? [] : ['ALL_EXECUTION']);

                let finalPermissions = [];
                let finalBlocked = [];

                if (outcomes.blocked_actions) {
                    finalBlocked = outcomes.blocked_actions;
                    finalPermissions = ['OBSERVE_ONLY'];
                } else if (outcomes.permissions) {
                    finalPermissions = outcomes.permissions;
                } else if (outcomes.constraints) {
                    // Interpret constraints as blocked actions in stress context
                    finalBlocked = outcomes.constraints;
                    finalPermissions = ['OBSERVE_ONLY'];
                }

                finalPolicyData = {
                    policy_state: pState,
                    permissions: finalPermissions,
                    blocked_actions: finalBlocked,
                    reason: `SIMULATION: ${activeScenario.condition_desc} [${outcomes.verdict || 'N/A'}]`,
                    epistemic_health: {
                        grade: meta?.epoch || 'SIM',
                        proxy_status: 'SIMULATED'
                    }
                };
            } else {
                // Scenario exists but no data for this market -> e.g. S3 only affects US
                finalPolicyData = {
                    policy_state: 'NORMAL',
                    permissions: ['ALL_ACTIONS'],
                    blocked_actions: [],
                    reason: `SIMULATION: No stress defined for ${market} in ${activeScenario.name}`,
                    epistemic_health: { grade: 'SIM', proxy_status: 'SIMULATED' }
                };
            }
        } else {
            // Loading or selection pending
            finalPolicyData = null;
        }
    }

    if (error && !isInspectionMode) {
        return (
            <div className="policy-card error">
                <div className="policy-header">
                    <h3>Governance Policy</h3>
                    <span className="badge offline">OFFLINE</span>
                </div>
                <div className="policy-body">
                    <p>Unable to load Active Policy.</p>
                    <pre>{error}</pre>
                </div>
            </div>
        )
    }

    if (!finalPolicyData) {
        return (
            <div className="policy-card loading">
                <h3>Loading Policy...</h3>
            </div>
        )
    }

    const { policy_state, permissions, blocked_actions, reason, epistemic_health } = finalPolicyData;
    const isHealthy = epistemic_health?.proxy_status === 'CANONICAL' || isSimulated;

    // Status Colors
    let statusClass = 'neutral';
    if (policy_state === 'ACTIVE') statusClass = 'active';
    if (policy_state === 'RESTRICTED') statusClass = 'restricted';
    if (policy_state === 'HALTED') statusClass = 'halted';

    return (
        <div className={`policy-card ${statusClass}`}>
            <div className="policy-header">
                <div className="title-row">
                    <h3>Decision Policy [{market}]</h3>
                    <span className={`status-badge ${statusClass}`}>{policy_state}</span>
                </div>
                <div className="meta-row">
                    <span className="epoch-tag">Epoch: {epistemic_health?.grade}</span>
                    <span className={`proxy-tag ${isHealthy ? 'good' : 'bad'}`}>
                        Proxy: {epistemic_health?.proxy_status}
                    </span>
                </div>
            </div>

            <div className="policy-body">
                <div className="reason-box">
                    <strong>Rationale:</strong> {reason}
                </div>

                <div className="permissions-grid">
                    <div className="perm-col allowed">
                        <h4>ALLOWED</h4>
                        {permissions.length === 0 && <span className="empty-tag">None</span>}
                        <ul>
                            {permissions.map(p => <li key={p}>{p}</li>)}
                        </ul>
                    </div>
                    <div className="perm-col blocked">
                        <h4>BLOCKED</h4>
                        {blocked_actions.length === 0 && <span className="empty-tag">None</span>}
                        <ul>
                            {blocked_actions.map(b => <li key={b}>{b}</li>)}
                        </ul>
                    </div>
                </div>
            </div>

            {/* Degraded State Warning Overlay if needed */}
            {epistemic_health?.proxy_status === 'DEGRADED' && (
                <div className="degraded-overlay">
                    <span>⚠️ DEGRADED PROXY STATE — OBSERVE ONLY</span>
                </div>
            )}
        </div>
    );
};

export default PolicyStateCard;
