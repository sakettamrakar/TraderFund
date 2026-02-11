import React, { useState, useEffect } from 'react';
import { getMarketFragility } from '../services/api';
import { useInspection } from '../context/InspectionContext';
import './FragilityStateCard.css';

const FragilityStateCard = ({ market }) => {
    const [fragilityData, setFragilityData] = useState(null);
    const [error, setError] = useState(null);
    const { isInspectionMode, activeScenario, meta } = useInspection();

    useEffect(() => {
        if (!isInspectionMode) {
            getMarketFragility(market)
                .then(data => {
                    setFragilityData(data.fragility); // Assuming API returns structure { fragility: ... }
                    setError(null);
                })
                .catch(err => {
                    console.error(err);
                    setError(err.message);
                    setFragilityData(null);
                });
        }
    }, [market, isInspectionMode]);

    let finalFragilityData = isInspectionMode ? null : fragilityData;

    if (isInspectionMode) {
        if (activeScenario) {
            const outcomes = activeScenario.markets?.[market]?.outcomes;
            if (outcomes) {
                // Synthesize Fragility Object
                const stressState = outcomes.stress_state || 'Systemic Stress (Simulated)';
                const constraints = outcomes.constraints || []; // e.g. ['ALLOW_LONG_ENTRY'] interpreted as subtracted? Or remaining?
                // The audit report lists "Constraints: [...]". Logic usually implies active limitations.
                // But S1 says "Constraints: ['ALLOW_LONG_ENTRY']". 
                // Fragility card expects `constraints_applied` (subtracted).
                // If S1 BLOCKS most things, then `ALLOW_LONG_ENTRY` is weird as a constraint.
                // Usually "Constraints" means "These rules constrain the system".
                // Let's treat them as Active Constraints.

                finalFragilityData = {
                    stress_state: stressState,
                    constraints_applied: constraints,
                    final_authorized_intents: outcomes.permissions || ['OBSERVE_ONLY'],
                    reason: `SIMULATION: ${activeScenario.condition_desc} [${outcomes.verdict || 'N/A'}]`
                };
            } else {
                // Scenario exists but no specific market data
                finalFragilityData = {
                    stress_state: 'NORMAL (SIM)',
                    constraints_applied: [],
                    final_authorized_intents: ['ALL'],
                    reason: `SIMULATION: No stress defined for ${market}`
                };
            }
        } else {
            // Loading or selection pending
            finalFragilityData = null;
        }
    }

    if (error && !isInspectionMode) {
        return (
            <div className="fragility-card error">
                <div className="fragility-header">
                    <h3>Fragility Policy</h3>
                    <span className="badge offline">OFFLINE</span>
                </div>
            </div>
        )
    }

    if (!finalFragilityData) {
        return (
            <div className="fragility-card loading">
                <div className="fragility-header">
                    <h3>Fragility Policy</h3>
                    <span className="badge">LOADING...</span>
                </div>
            </div>
        )
    }

    const { stress_state, constraints_applied, final_authorized_intents, reason } = finalFragilityData;

    let statusClass = 'normal';
    // Mapping various potential strings
    const s = stressState => stressState?.toUpperCase().replace(' ', '_');
    if (s(stress_state).includes('SYSTEMIC')) statusClass = 'systemic';
    if (s(stress_state).includes('ELEVATED')) statusClass = 'elevated';
    if (s(stress_state).includes('TRANSITION')) statusClass = 'transition';
    if (s(stress_state).includes('NOT_EVALUATED') || s(stress_state).includes('NORMAL')) statusClass = 'neutral';

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
