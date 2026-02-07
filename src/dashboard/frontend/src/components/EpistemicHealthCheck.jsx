import React, { useState, useEffect } from 'react';
import { getIntelligenceSnapshot } from '../services/api';
// Minimal Component for Epistemic Health (Proxy Status & Epoch)
// Used in SystemStatus or other high-level views to ensure purity visibility

const EpistemicHealthCheck = ({ market }) => {
    const [health, setHealth] = useState(null);

    useEffect(() => {
        // We reuse the Intelligence/Policy endpoint as it contains the epistemic health
        const fetchHealth = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/intelligence/policy/${market}`);
                if (response.ok) {
                    const data = await response.json();
                    setHealth(data.policy_decision?.epistemic_health);
                }
            } catch (e) {
                console.error("Epistemic Check Failed:", e);
            }
        };
        fetchHealth();
        const interval = setInterval(fetchHealth, 60000);
        return () => clearInterval(interval);
    }, [market]);

    if (!health) return <div className="epistemic-check loading">Checking Truth...</div>;

    const isCanonical = health.proxy_status === 'CANONICAL';

    return (
        <div className={`epistemic-check ${isCanonical ? 'canonical' : 'degraded'}`}>
            <div className="health-row">
                <span className="label">TRUTH EPOCH:</span>
                <span className="value">{health.grade}</span>
            </div>
            <div className="health-row">
                <span className="label">PROXY STATUS:</span>
                <span className="value">{health.proxy_status}</span>
            </div>
        </div>
    );
};

export default EpistemicHealthCheck;
