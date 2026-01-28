import React, { useEffect, useState } from 'react';
import { getSystemNarrative } from '../services/api';
import './SystemNarrative.css';

const SystemNarrative = () => {
    const [narrative, setNarrative] = useState(null);

    useEffect(() => {
        getSystemNarrative().then(setNarrative).catch(console.error);
    }, []);

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
