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
export const getCombinedPortfolio = async () => (await api.get('/portfolio/combined')).data;
