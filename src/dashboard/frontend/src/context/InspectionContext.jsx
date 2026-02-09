import React, { createContext, useContext, useState, useEffect } from 'react';
import { getStressScenarios } from '../services/api';

const InspectionContext = createContext();

export const useInspection = () => useContext(InspectionContext);

export const InspectionProvider = ({ children }) => {
    const [isInspectionMode, setIsInspectionMode] = useState(false);
    const [scenarios, setScenarios] = useState([]);
    const [selectedScenarioId, setSelectedScenarioId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [meta, setMeta] = useState(null);

    const toggleInspection = async () => {
        if (!isInspectionMode) {
            // Activate Inspection
            setLoading(true);
            try {
                const data = await getStressScenarios();
                if (data.error) {
                    setError(data.error);
                    // Fail-safe: abort activation
                    setIsInspectionMode(false);
                } else {
                    setScenarios(data.scenarios || []);
                    setMeta(data.trace);
                    if (data.scenarios && data.scenarios.length > 0) {
                        setSelectedScenarioId(data.scenarios[0].id);
                    }
                    setIsInspectionMode(true);
                }
            } catch (err) {
                console.error("Failed to load scenarios", err);
                setError("Failed to load scenarios");
                setIsInspectionMode(false);
            } finally {
                setLoading(false);
            }
        } else {
            // Teardown - Explicit Exit without Refresh
            setIsInspectionMode(false);

            // Clean state
            setScenarios([]);
            setSelectedScenarioId(null);
            setMeta(null);
            setError(null);
            // Components subscribed to isInspectionMode will handle re-fetch via useEffect
        }
    };

    const selectScenario = (id) => setSelectedScenarioId(id);

    const activeScenario = scenarios.find(s => s.id === selectedScenarioId);

    // Hard Safety: If mode is on, verify scenarios loaded or fallback
    useEffect(() => {
        if (isInspectionMode && scenarios.length === 0 && !loading) {
            // Something wrong, exit
            setIsInspectionMode(false);
        }
    }, [isInspectionMode, scenarios, loading]);

    return (
        <InspectionContext.Provider value={{
            isInspectionMode,
            scenarios,
            selectedScenarioId,
            selectScenario,
            toggleInspection,
            activeScenario,
            meta,
            loading,
            error
        }}>
            {children}
        </InspectionContext.Provider>
    );
};
