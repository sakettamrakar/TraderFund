import React, { useEffect, useState } from 'react';
import { getSystemStressPosture, getSystemConstraintPosture } from '../services/api';
import './SystemPosture.css';

const SystemPosture = () => {
    const [stressData, setStressData] = useState(null);
    const [constraintData, setConstraintData] = useState(null);

    useEffect(() => {
        getSystemStressPosture().then(setStressData).catch(console.error);
        getSystemConstraintPosture().then(setConstraintData).catch(console.error);
    }, []);

    const stressPosture = stressData?.posture?.system_stress_posture || 'UNKNOWN';
    const constraintPosture = constraintData?.posture?.system_constraint_posture || 'UNKNOWN';

    const getPostureClass = (val) => val.toLowerCase().replace('_', '-');

    return (
        <div className="system-posture-container">
            {/* A2.1: System Stress Posture */}
            <div className={`posture-widget stress ${getPostureClass(stressPosture)}`}>
                <div className="widget-header">
                    <span className="widget-id">A2.1</span>
                    <span className="widget-label">SYSTEM STRESS POSTURE</span>
                </div>
                <div className="posture-value">{stressPosture}</div>
                <div className="posture-decomposition">
                    {stressData?.posture?.derived_from && Object.entries(stressData.posture.derived_from).map(([m, s]) => (
                        <div key={m} className="decomp-item">
                            <span className="decomp-market">{m}:</span>
                            <span className="decomp-state">{s}</span>
                        </div>
                    ))}
                </div>
                <div className="trace-badge">
                    Source: {stressData?.trace?.source} | Epoch: {stressData?.posture?.truth_epoch || 'N/A'}
                </div>
            </div>

            {/* A2.2: System Constraint Posture */}
            <div className={`posture-widget constraint ${getPostureClass(constraintPosture)}`}>
                <div className="widget-header">
                    <span className="widget-id">A2.2</span>
                    <span className="widget-label">SYSTEM CONSTRAINT POSTURE</span>
                </div>
                <div className="posture-value">{constraintPosture}</div>
                <div className="posture-decomposition">
                    {constraintData?.posture?.derived_from && Object.entries(constraintData.posture.derived_from).map(([m, d]) => (
                        <div key={m} className="decomp-item">
                            <span className="decomp-market">{m}:</span>
                            <span className="decomp-state">{d.permissions?.join(', ') || 'NONE'}</span>
                        </div>
                    ))}
                </div>
                <div className="trace-badge">
                    Source: {constraintData?.trace?.source} | Epoch: {constraintData?.posture?.truth_epoch || 'N/A'}
                </div>
            </div>
        </div>
    );
};

export default SystemPosture;
