import axios from 'axios';

const api = axios.create({
    baseURL: '/api' // Proxied by Vite to localhost:8000
});

export const getSystemStatus = async () => (await api.get('/system/status')).data;
export const getLayerHealth = async () => (await api.get('/layers/health')).data;
export const getMarketSnapshot = async () => (await api.get('/market/snapshot')).data;
export const getWatcherTimeline = async () => (await api.get('/watchers/timeline')).data;
export const getStrategyEligibility = async () => (await api.get('/strategies/eligibility')).data;
export const getMetaSummary = async () => (await api.get('/meta/summary')).data;
export const getSystemNarrative = async () => (await api.get('/system/narrative')).data;
export const getSystemBlockers = async () => (await api.get('/system/blockers')).data;
export const getCapitalReadiness = async () => (await api.get('/capital/readiness')).data;
export const getCapitalHistory = async () => (await api.get('/capital/history')).data;
export const getMacroContext = async () => (await api.get('/macro/context')).data;

export default api;
