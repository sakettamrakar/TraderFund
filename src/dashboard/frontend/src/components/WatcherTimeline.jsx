import React, { useEffect, useState } from 'react';
import { getWatcherTimeline } from '../services/api';
import './WatcherTimeline.css';

const WatcherTimeline = () => {
    const [timeline, setTimeline] = useState([]);

    useEffect(() => {
        getWatcherTimeline().then(data => setTimeline(data.history || [])).catch(console.error);
    }, []);

    if (!timeline || !timeline.length) return <div>No Timeline Data</div>;

    return (
        <div className="watcher-timeline">
            <h3>Diagnostic Timeline (Last 10 Ticks)</h3>
            <table className="timeline-table">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Momentum</th>
                        <th>Expansion</th>
                        <th>Dispersion</th>
                        <th>Liquidity</th>
                    </tr>
                </thead>
                <tbody>
                    {timeline.map((t, i) => (
                        <tr key={i}>
                            <td className="time-col">
                                {t.timestamp ? new Date(t.timestamp).toLocaleString('en-US', {
                                    year: 'numeric', month: '2-digit', day: '2-digit',
                                    hour: '2-digit', minute: '2-digit', second: '2-digit',
                                    hour12: false
                                }) + " UTC" : 'N/A'}
                            </td>
                            <td className={`state-col ${t.momentum?.toLowerCase() || 'unknown'}`}>{t.momentum || 'N/A'}</td>
                            <td className={`state-col ${t.expansion?.toLowerCase() || 'unknown'}`}>{t.expansion || 'N/A'}</td>
                            <td className={`state-col ${t.dispersion?.toLowerCase() || 'unknown'}`}>{t.dispersion || 'N/A'}</td>
                            <td className={`state-col ${t.liquidity?.toLowerCase() || 'unknown'}`}>{t.liquidity || 'N/A'}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default WatcherTimeline;
