import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const getPortfolioOverview = async (market) => (await api.get(`/portfolio/overview/${market}`)).data;
export const getPortfolioHoldings = async (market, portfolioId) => (await api.get(`/portfolio/holdings/${market}/${portfolioId}`)).data;
export const getPortfolioDiversification = async (market, portfolioId) => (await api.get(`/portfolio/diversification/${market}/${portfolioId}`)).data;
export const getPortfolioRisk = async (market, portfolioId) => (await api.get(`/portfolio/risk/${market}/${portfolioId}`)).data;
export const getPortfolioInsights = async (market, portfolioId) => (await api.get(`/portfolio/insights/${market}/${portfolioId}`)).data;
export const getPortfolioResilience = async (market, portfolioId) => (await api.get(`/portfolio/resilience/${market}/${portfolioId}`)).data;
export const getPortfolioExposure = async (market, portfolioId) => (await api.get(`/portfolio/exposure/${market}/${portfolioId}`)).data;
export const getPortfolioMacroAlignment = async (market, portfolioId) => (await api.get(`/portfolio/macro-alignment/${market}/${portfolioId}`)).data;
export const getPortfolioResearch = async (market, portfolioId) => (await api.get(`/portfolio/research/${market}/${portfolioId}`)).data;
export const getPortfolioAdvisory = async (market, portfolioId) => (await api.get(`/portfolio/advisory/${market}/${portfolioId}`)).data;
export const getPortfolioRefreshStatus = async (market, portfolioId) => (await api.get(`/portfolio/refresh-status/${market}/${portfolioId}`)).data;
export const getPortfolioTrend = async (market, portfolioId, limit = 20) => (await api.get(`/portfolio/trend/${market}/${portfolioId}`, { params: { limit } })).data;
export const triggerPortfolioRefresh = async (market, portfolioId, options = {}) => (await api.post(`/portfolio/refresh/${market}/${portfolioId}`, null, { params: options })).data;
export const getCombinedPortfolio = async () => (await api.get('/portfolio/combined')).data;
