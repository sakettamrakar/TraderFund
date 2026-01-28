import React, { useEffect, useState } from 'react';
import { getSystemStatus } from '../services/api';
import './SystemStatus.css';

const SystemStatus = () => {
    const [data, setData] = useState(null);

    useEffect(() => {
        getSystemStatus().then(setData).catch(console.error);
    }, []);

    if (!data) return <div className="status-banner loading">Loading System Status...</div>;

    const statusClass = `status-tag ${data.system_state?.toLowerCase() || 'idle'}`;

    // Alerting Logic: Check Staleness (e.g. > 20 mins)
    const lastTickTime = new Date(data.last_ev_tick);
    const now = new Date();
    const minutesSince = (now - lastTickTime) / 60000;
    const isStale = !isNaN(minutesSince) && minutesSince > 20;

    return (
        <div className="system-status_wrapper">
            {isStale && (
                <div className="alert-banner error">
                    ⚠️ DATA STALE: Last tick was {Math.round(minutesSince)} mins ago. Check Scheduler.
                </div>
            )}
            <div className="system-status-banner">
                <div className="status-main">
                    <span className="label">SYSTEM STATE</span>
                    <span className={statusClass}>{data.system_state}</span>
                    <span className="reason">{data.reason}</span>
                </div>
                <div className="status-meta">
                    <div className="meta-item">
                        <span className="meta-label">LAST TICK</span>
                        <span className={`meta-value ${isStale ? 'stale' : ''}`}>{data.last_ev_tick}</span>
                    </div>
                    <div className="meta-item">
                        <span className="meta-label">GOVERNANCE</span>
                        <span className="meta-value governance-clean">{data.governance_status}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SystemStatus;
