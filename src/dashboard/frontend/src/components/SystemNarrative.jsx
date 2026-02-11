import React, { useEffect, useState } from 'react';
import { getSystemNarrative } from '../services/api';
import { useInspection } from '../context/InspectionContext';
import './SystemNarrative.css';

const SystemNarrative = ({ market }) => {
    const [narrative, setNarrative] = useState(null);
    const { isInspectionMode, activeScenario } = useInspection();

    useEffect(() => {
        if (!isInspectionMode) {
            getSystemNarrative(market).then(setNarrative).catch(console.error);
        } else if (activeScenario) {
            setNarrative({
                narrative_mode: 'EVIDENCE_ONLY',
                tone: 'STRESS_TEST',
                posture: 'SIMULATED',
                gating_reason: 'Inspection scenario is active. Live truth narrative is intentionally suppressed.',
                summary: `STRESS SCENARIO ${activeScenario.id}: ${activeScenario.condition_desc}. This constitutes a theoretical simulation for stress testing purposes only. Live data is suppressed.`
            });
        }
    }, [market, isInspectionMode, activeScenario]);

    if (!narrative && !isInspectionMode) return <div className="loading-narrative">Loading system narrative...</div>;
    // Handle loading during inspection scenario switch
    if (!narrative && isInspectionMode) return <div className="loading-narrative">Loading scenario...</div>;

    const mode = narrative?.narrative_mode || 'UNKNOWN';
    const gatingReason = narrative?.gating_reason || narrative?.silence_reason || null;
    const refs = narrative?.provenance_references || narrative?.citations || [];

    return (
        <div className="system-narrative-panel">
            <div className="narrative-badge">
                <span className="mode-indicator">Mode: {mode}</span>
                <span className="tone-indicator">Tone: {narrative.tone}</span>
                <span className="posture-indicator">Posture: {narrative.posture}</span>
            </div>

            {mode === 'SILENCED' ? (
                <p className="narrative-silenced">NARRATIVE SILENCED</p>
            ) : (
                <p className="narrative-text">{narrative.summary}</p>
            )}

            {gatingReason && <p className="narrative-gating">Gating Reason: {gatingReason}</p>}

            {refs.length > 0 && (
                <div className="narrative-provenance">
                    <div className="provenance-title">Provenance</div>
                    <ul className="provenance-list">
                        {refs.slice(0, 6).map((ref) => (
                            <li key={ref}>{ref}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default SystemNarrative;
