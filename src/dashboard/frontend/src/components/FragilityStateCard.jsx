import React, { useState, useEffect } from 'react';
import './FragilityStateCard.css';

const FragilityStateCard = ({ market }) => {
    const [fragilityData, setFragilityData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchFragility = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/intelligence/fragility/${market}`);
                if (!response.ok) throw new Error("Fragility fetch failed");
                const data = await response.json();
                setFragilityData(data.fragility_context);
                setError(null);
            } catch (err) {
                console.error(err);
                setError(err.message);
            }
        };

        fetchFragility();
        const interval = setInterval(fetchFragility, 30000);
        return () => clearInterval(interval);
    }, [market]);

    if (error || !fragilityData) {
        return (
            <div className="fragility-card error">
                <div className="fragility-header">
                    <h3>Fragility Policy</h3>
                    <span className="badge offline">OFFLINE</span>
                </div>
            </div>
        )
    }

    const { stress_state, constraints_applied, final_authorized_intents, reason } = fragilityData;

    let statusClass = 'normal';
    if (stress_state === 'SYSTEMIC_STRESS') statusClass = 'systemic';
    if (stress_state === 'ELEVATED_STRESS') statusClass = 'elevated';
    if (stress_state === 'TRANSITION_UNCERTAIN') statusClass = 'transition';
    if (stress_state === 'NOT_EVALUATED') statusClass = 'neutral';

    return (
        <div className={`fragility-card ${statusClass}`}>
            <div className="fragility-header">
                <div className="title-row">
                    <h3>Fragility & Stress [{market}]</h3>
                    <span className={`status-badge ${statusClass}`}>{stress_state}</span>
                </div>
            </div>

            <div className="fragility-body">
                <div className="reason-box">
                    <strong>Stress Reason:</strong> {reason}
                </div>

                <div className="constraints-section">
                    <h4>CONSTRAINTS APPLIED (SUBTRACTED)</h4>
                    {constraints_applied.length === 0 ? <span className="empty-tag">None</span> : (
                        <ul className="blocked-list">
                            {constraints_applied.map(c => <li key={c}>{c}</li>)}
                        </ul>
                    )}
                </div>

                <div className="final-intents">
                    <h4>FINAL AUTHORIZED INTENTS</h4>
                    <div className="intent-chips">
                        {final_authorized_intents.map(i => <span key={i} className="intent-chip">{i}</span>)}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FragilityStateCard;
