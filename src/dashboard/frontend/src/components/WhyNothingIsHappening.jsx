import React, { useEffect, useState } from 'react';
import { getSystemBlockers } from '../services/api';
import './WhyNothingIsHappening.css';

const WhyNothingIsHappening = () => {
    const [blockers, setBlockers] = useState([]);

    useEffect(() => {
        getSystemBlockers().then(setBlockers).catch(console.error);
    }, []);

    if (!blockers || blockers.length === 0) return null;

    return (
        <div className="why-panel">
            <h3 className="why-title">Why Nothing Is Happening</h3>
            <div className="blocker-checklist">
                {blockers.map((b) => (
                    <div key={b.id} className={`blocker-item ${b.passed ? 'passed' : 'blocked'}`}>
                        <div className="blocker-status-icon">
                            {b.passed ? '✅' : '🔒'}
                        </div>
                        <div className="blocker-info">
                            <span className="blocker-label">{b.label}</span>
                            <span className="blocker-reason">{b.reason}</span>
                        </div>
                    </div>
                ))}
            </div>
            <div className="why-footer">
                * This explanation reflects the current truth epoch (TE-2026-01-30) only and does not imply future action.
            </div>
        </div>
    );
};

export default WhyNothingIsHappening;
