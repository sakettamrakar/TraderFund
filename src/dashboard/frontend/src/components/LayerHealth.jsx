import React, { useEffect, useState } from 'react';
import { getLayerHealth } from '../services/api';
import './LayerHealth.css';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const LayerHealth = ({ market }) => {
    const [health, setHealth] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        getLayerHealth(market).then(res => {
            setHealth(res);
            setLoading(false);
        }).catch(console.error);
    }, [market]);

    if (loading) return <div className="layer-health-panel loading">Loading Layer Health...</div>;
    if (health?.error) return <div className="health-error">Governance Error: {health.error}</div>;

    // Filter out metadata and system keys
    const layers = Object.entries(health || {})
        .filter(([name]) => !name.startsWith('_') && name !== 'error')
        .map(([name, data]) => ({
            name,
            ...data
        }));

    const meta = health?._meta || {};

    const getStatusIcon = (status) => {
        switch (status) {
            case 'HEALTHY':
            case 'CANONICAL':
                return <CheckCircle size={14} className="icon-healthy" />;
            case 'FROZEN':
                return <CheckCircle size={14} className="icon-frozen" />;
            case 'LOCKED':
            case 'DISABLED':
                return <XCircle size={14} className="icon-locked" />;
            default:
                return <AlertTriangle size={14} className="icon-warning" />;
        }
    };

    return (
        <div className="layer-health-panel">
            <div className="panel-header">
                <span className="role-id">A0.1</span>
                <h3>System Layer Health</h3>
            </div>
            <div className="health-grid">
                {layers.map((layer) => (
                    <div key={layer.name} className={`health-card status-${layer.status?.toLowerCase()}`}>
                        <div className="card-header">
                            <span className="layer-name">{layer.name}</span>
                            {getStatusIcon(layer.status)}
                        </div>
                        <div className="card-footer">
                            <span className="status-text">{layer.status}</span>
                        </div>
                    </div>
                ))}
            </div>
            <div className="trace-footer">
                <div className="trace-badge">A0.1 | Epoch: {meta.truth_epoch} | Source: docs/intelligence/system_layer_health.json</div>
            </div>
        </div>
    );
};

export default LayerHealth;
