import React, { useEffect, useState } from 'react';
import { getLayerHealth } from '../services/api';
import './LayerHealth.css';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const LayerHealth = () => {
    const [layers, setLayers] = useState(null);

    useEffect(() => {
        getLayerHealth().then(setLayers).catch(console.error);
    }, []);

    if (!layers || !layers.layers) return <div>Loading...</div>;

    return (
        <div className="layer-health-panel">
            <h3>System Layer Health</h3>
            <div className="health-grid">
                {layers.layers.map((layer) => (
                    <div key={layer.name} className={`health-card ${layer.status?.toLowerCase() || 'unknown'}`}>
                        <div className="card-header">
                            <span className="layer-name">{layer.name}</span>
                            {layer.status === 'OK' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                        </div>
                        <div className="card-footer">
                            <span className="last-updated">{layer.last_updated ? new Date(layer.last_updated).toLocaleTimeString() : 'N/A'}</span>
                            <span className="status-text">{layer.status}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LayerHealth;
