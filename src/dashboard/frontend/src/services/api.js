import axios from 'axios';

const api = axios.create({
    baseURL: '/api' // Proxied by Vite to localhost:8000
});

export const getSystemStatus = async (market) => (await api.get(`/system/status?market=${market}`)).data;
export const getLayerHealth = async (market) => (await api.get(`/layers/health?market=${market}`)).data;
export const getMarketSnapshot = async (market) => (await api.get(`/market/snapshot?market=${market}`)).data;
export const getWatcherTimeline = async (market) => (await api.get(`/watchers/timeline?market=${market}`)).data;
export const getStrategyEligibility = async (market) => (await api.get(`/strategies/eligibility?market=${market}`)).data;
export const getMetaSummary = async () => (await api.get('/meta/summary')).data; // Global
export const getSystemNarrative = async () => (await api.get('/system/narrative')).data; // Likely Global or need review
export const getSystemBlockers = async () => (await api.get('/system/blockers')).data; // Likely Global
export const getCapitalReadiness = async (market) => (await api.get(`/capital/readiness?market=${market}`)).data;
export const getCapitalHistory = async (market) => (await api.get(`/capital/history?market=${market}`)).data;
export const getMacroContext = async (market) => (await api.get(`/macro/context?market=${market}`)).data; // Wait, api.py doesn't have this yet?
export const getMarketParity = async (market) => (await api.get(`/intelligence/parity/${market}`)).data;
export const getMarketPolicy = async (market) => (await api.get(`/intelligence/policy/${market}`)).data;
export const getMarketFragility = async (market) => (await api.get(`/intelligence/fragility/${market}`)).data;
export const getEvaluationScope = async () => (await api.get('/meta/evaluation/scope')).data;
export const getSystemStressPosture = async () => (await api.get('/intelligence/stress_posture')).data;
export const getSystemConstraintPosture = async () => (await api.get('/intelligence/constraint_posture')).data;
export const getExecutionGate = async () => (await api.get('/intelligence/gate')).data;
export const getIntelligenceSnapshot = async (market) => (await api.get(`/intelligence/snapshot?market=${market}`)).data;

export default api;
