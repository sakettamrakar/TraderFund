import React, { useEffect, useState } from 'react';
import { getSystemStressPosture, getSystemConstraintPosture } from '../services/api';
import { useInspection } from '../context/InspectionContext';
import './SystemPosture.css';

const SystemPosture = () => {
    const [stressData, setStressData] = useState(null);
    const [constraintData, setConstraintData] = useState(null);
    const { isInspectionMode, activeScenario, meta } = useInspection();

    useEffect(() => {
        if (!isInspectionMode) {
            getSystemStressPosture().then(setStressData).catch(console.error);
            getSystemConstraintPosture().then(setConstraintData).catch(console.error);
        }
    }, [isInspectionMode]);

    let finalStressData = isInspectionMode ? null : stressData;
    let finalConstraintData = isInspectionMode ? null : constraintData;

    if (isInspectionMode) {
        if (activeScenario) {
            // Synthesize Inspection Data for A2.1
            const markets = activeScenario.markets || {};
            const indiaStress = markets.INDIA?.outcomes?.stress_state || 'NORMAL';
            const usStress = markets.US?.outcomes?.stress_state || 'NORMAL';

            // Simple logic: Critical > Stressed > Normal
            let globalStress = 'NORMAL';
            if (indiaStress === 'SYSTEMIC_STRESS' || usStress === 'SYSTEMIC_STRESS') globalStress = 'SYSTEMIC_STRESS';
            else if (indiaStress === 'STRESSED' || usStress === 'STRESSED') globalStress = 'STRESSED';

            finalStressData = {
                posture: {
                    system_stress_posture: globalStress,
                    derived_from: { INDIA: indiaStress, US: usStress },
                    truth_epoch: meta?.epoch || 'INSPECTION',
                    is_simulation: true
                },
                trace: { source: meta?.source || 'Scenario Report' }
            };

            // Synthesize Inspection Data for A2.2
            const indiaConstraints = markets.INDIA?.outcomes?.constraints || [];
            const usConstraints = markets.US?.outcomes?.constraints || [];

            let globalConstraint = 'NORMAL';
            if (globalStress !== 'NORMAL') globalConstraint = 'RESTRICTED';
            if (globalStress === 'SYSTEMIC_STRESS') globalConstraint = 'HALTED';

            finalConstraintData = {
                posture: {
                    system_constraint_posture: globalConstraint,
                    derived_from: {
                        INDIA: { permissions: indiaConstraints },
                        US: { permissions: usConstraints }
                    },
                    truth_epoch: meta?.epoch || 'INSPECTION',
                    is_simulation: true
                },
                trace: { source: meta?.source || 'Scenario Report' }
            };
        } else {
            // Scenario not selected or loading -> Explicit Unavailable
            finalStressData = { posture: { system_stress_posture: 'UNAVAILABLE' }, trace: { source: 'N/A' } };
            finalConstraintData = { posture: { system_constraint_posture: 'UNAVAILABLE' }, trace: { source: 'N/A' } };
        }
    }

    const stressPosture = finalStressData?.posture?.system_stress_posture || 'UNKNOWN';
    const constraintPosture = finalConstraintData?.posture?.system_constraint_posture || 'UNKNOWN';

    const getPostureClass = (val) => val.toLowerCase().replace('_', '-');

    return (
        <div className={`system-posture-container ${isInspectionMode ? 'inspection-mode' : ''}`}>
            {isInspectionMode && <div className="inspection-banner">INSPECTION MODE — SCENARIO VISUALIZATION</div>}

            {/* A2.1: System Stress Posture */}
            <div className={`posture-widget stress ${getPostureClass(stressPosture)}`}>
                <div className="widget-header">
                    <span className="widget-id">A2.1</span>
                    <span className="widget-label">SYSTEM STRESS POSTURE</span>
                    {isInspectionMode && <span className="sim-badge">SIM</span>}
                </div>
                <div className="posture-value">{stressPosture}</div>
                <div className="posture-decomposition">
                    {finalStressData?.posture?.derived_from && Object.entries(finalStressData.posture.derived_from).map(([m, s]) => (
                        <div key={m} className="decomp-item">
                            <span className="decomp-market">{m}:</span>
                            <span className="decomp-state">{s}</span>
                        </div>
                    ))}
                </div>
                <div className="trace-badge">
                    Source: {finalStressData?.trace?.source} | Epoch: {finalStressData?.posture?.truth_epoch || 'N/A'}
                </div>
            </div>

            {/* A2.2: System Constraint Posture */}
            <div className={`posture-widget constraint ${getPostureClass(constraintPosture)}`}>
                <div className="widget-header">
                    <span className="widget-id">A2.2</span>
                    <span className="widget-label">SYSTEM CONSTRAINT POSTURE</span>
                    {isInspectionMode && <span className="sim-badge">SIM</span>}
                </div>
                <div className="posture-value">{constraintPosture}</div>
                <div className="posture-decomposition">
                    {finalConstraintData?.posture?.derived_from && Object.entries(finalConstraintData.posture.derived_from).map(([m, d]) => (
                        <div key={m} className="decomp-item">
                            <span className="decomp-market">{m}:</span>
                            <span className="decomp-state">{d.permissions ? (Array.isArray(d.permissions) ? d.permissions.join(', ') : d.permissions) : d}</span>
                        </div>
                    ))}
                </div>
                <div className="trace-badge">
                    Source: {finalConstraintData?.trace?.source} | Epoch: {finalConstraintData?.posture?.truth_epoch || 'N/A'}
                </div>
            </div>
        </div>
    );
};

export default SystemPosture;
