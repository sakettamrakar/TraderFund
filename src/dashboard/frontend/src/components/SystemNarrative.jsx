import React, { useEffect, useState } from 'react';
import { getSystemNarrative } from '../services/api';
import './SystemNarrative.css';

const SystemNarrative = ({ market }) => {
    const [narrative, setNarrative] = useState(null);

    useEffect(() => {
        // Narrative is currently global, but we re-fetch on market switch
        // to ensure freshness if context switches.
        getSystemNarrative().then(setNarrative).catch(console.error);
    }, [market]);

    if (!narrative) return <div className="loading-narrative">Loading system narrative...</div>;

    return (
        <div className="system-narrative-panel">
            <div className="narrative-badge">
                <span className="tone-indicator">Tone: {narrative.tone}</span>
                <span className="posture-indicator">Posture: {narrative.posture}</span>
            </div>
            <p className="narrative-text">{narrative.summary}</p>
        </div>
    );
};

export default SystemNarrative;
