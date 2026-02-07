import React, { useState, useEffect } from 'react';
import './PolicyStateCard.css';

const PolicyStateCard = ({ market }) => {
    const [policyData, setPolicyData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Determine file limit based on market
        // In production, this would be an API call. 
        // Here we assume the backend serves these JSONs statically or we fetch directly if possible.
        // For this environment, we'll try to fetch from the known backend endpoint or assume static mapping.

        const fetchPolicy = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/intelligence/policy/${market}`);
                if (!response.ok) {
                    // Determine if it's 404 (Not Found) or 500
                    if (response.status === 404) {
                        throw new Error("Policy not found.");
                    }
                    throw new Error("Policy fetch failed");
                }
                const data = await response.json();
                setPolicyData(data.policy_decision);
                setError(null);
            } catch (err) {
                console.error(err);
                setError(err.message);
                // Fallback for demo if API not running (Simulation logic)
                // Ideally we don't simulate, but for UI robustness:
                setPolicyData(null);
            }
        };

        fetchPolicy();
        // Poll every 30s
        const interval = setInterval(fetchPolicy, 30000);
        return () => clearInterval(interval);

    }, [market]);

    if (error) {
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

    if (!policyData) {
        return (
            <div className="policy-card loading">
                <h3>Loading Policy...</h3>
            </div>
        )
    }

    const { policy_state, permissions, blocked_actions, reason, epistemic_health } = policyData;
    const isHealthy = epistemic_health?.proxy_status === 'CANONICAL';

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
