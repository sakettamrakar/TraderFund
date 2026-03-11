import React, { useEffect, useState } from 'react';
import {
  getCombinedPortfolio,
  getPortfolioDiversification,
  getPortfolioHoldings,
  getPortfolioInsights,
  getPortfolioOverview,
  getPortfolioResilience,
  getPortfolioRisk,
} from '../services/portfolioApi';
import './PortfolioIntelligencePanel.css';

const PortfolioIntelligencePanel = ({ market }) => {
  const [overview, setOverview] = useState(null);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState(null);
  const [holdings, setHoldings] = useState(null);
  const [diversification, setDiversification] = useState(null);
  const [risk, setRisk] = useState(null);
  const [insights, setInsights] = useState(null);
  const [resilience, setResilience] = useState(null);
  const [combined, setCombined] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    setOverview(null);
    setHoldings(null);
    setDiversification(null);
    setRisk(null);
    setInsights(null);
    setResilience(null);
    Promise.all([
      getPortfolioOverview(market),
      getCombinedPortfolio(),
    ])
      .then(([overviewPayload, combinedPayload]) => {
        setOverview(overviewPayload);
        setCombined(combinedPayload);
        const firstPortfolio = overviewPayload?.portfolios?.[0]?.portfolio_id || null;
        setSelectedPortfolioId(firstPortfolio);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
      });
  }, [market]);

  useEffect(() => {
    if (!selectedPortfolioId) {
      return;
    }
    Promise.all([
      getPortfolioHoldings(market, selectedPortfolioId),
      getPortfolioDiversification(market, selectedPortfolioId),
      getPortfolioRisk(market, selectedPortfolioId),
      getPortfolioInsights(market, selectedPortfolioId),
      getPortfolioResilience(market, selectedPortfolioId),
    ])
      .then(([holdingsPayload, diversificationPayload, riskPayload, insightsPayload, resiliencePayload]) => {
        setHoldings(holdingsPayload);
        setDiversification(diversificationPayload);
        setRisk(riskPayload);
        setInsights(insightsPayload);
        setResilience(resiliencePayload);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
      });
  }, [market, selectedPortfolioId]);

  const portfolios = overview?.portfolios || [];
  const selectedPortfolio = portfolios.find((portfolio) => portfolio.portfolio_id === selectedPortfolioId) || portfolios[0] || null;
  const topHoldings = holdings?.holdings?.slice(0, 8) || [];
  const insightRows = insights?.insights?.slice(0, 6) || [];
  const sectorBreakdown = diversification?.diversification?.sector_allocation || {};
  const factorBreakdown = diversification?.diversification?.factor_distribution || {};
  const portfolioDataSource = holdings?.portfolio_data_source || selectedPortfolio?.portfolio_data_source || 'UNAVAILABLE';
  const diagnostics = holdings?.refresh_diagnostics || selectedPortfolio?.refresh_diagnostics || {};
  const mcpDiagnostics = diagnostics?.mcp || {};
  const apiFallback = diagnostics?.api_fallback || {};

  return (
    <section className="portfolio-intelligence-panel">
      <div className="portfolio-intel-header">
        <div>
          <h3>Portfolio Intelligence</h3>
          <p>Read-only broker portfolio analytics with provenance and regime gating.</p>
        </div>
        <div className="portfolio-trace">
          <span>Epoch: {overview?.truth_epoch || 'TRUTH_EPOCH_2026-03-06_01'}</span>
          <span>Scope: {market}</span>
          <span>Source: {portfolioDataSource}</span>
        </div>
      </div>

      {error && <div className="portfolio-error">Portfolio intelligence unavailable: {error}</div>}

      {!error && portfolios.length === 0 && (
        <div className="portfolio-empty">
          <strong>No imported portfolios available for {market}.</strong>
          <span>Run the read-only tracker refresh outside the dashboard to populate analytics artifacts.</span>
        </div>
      )}

      {portfolios.length > 0 && (
        <>
          <div className="portfolio-overview-grid">
            <div className="portfolio-metric">
              <span>Total Value</span>
              <strong>{overview?.aggregated?.total_value?.toLocaleString?.() ?? overview?.aggregated?.total_value}</strong>
            </div>
            <div className="portfolio-metric">
              <span>Total PnL</span>
              <strong>{overview?.aggregated?.total_pnl?.toLocaleString?.() ?? overview?.aggregated?.total_pnl}</strong>
            </div>
            <div className="portfolio-metric">
              <span>Positions</span>
              <strong>{overview?.aggregated?.total_positions}</strong>
            </div>
            <div className="portfolio-metric">
              <span>Resilience</span>
              <strong>{overview?.aggregated?.resilience_score} {overview?.aggregated?.resilience_classification}</strong>
            </div>
          </div>

          <div className="portfolio-selector-row">
            {portfolios.map((portfolio) => (
              <button
                key={portfolio.portfolio_id}
                className={portfolio.portfolio_id === selectedPortfolioId ? 'active' : ''}
                onClick={() => setSelectedPortfolioId(portfolio.portfolio_id)}
              >
                {portfolio.display_name} [{portfolio.broker}]
              </button>
            ))}
          </div>

          <div className="portfolio-intel-grid">
            <div className="portfolio-card">
              <h4>Top Holdings</h4>
              <div className="portfolio-table">
                <div className="portfolio-table-header">
                  <span>Symbol</span>
                  <span>Weight</span>
                  <span>Conviction</span>
                  <span>Flags</span>
                </div>
                {topHoldings.map((item) => (
                  <div className="portfolio-table-row" key={`${item.ticker}-${item.asset_bucket || 'row'}`}>
                    <span>{item.ticker}</span>
                    <span>{item.weight_pct}%</span>
                    <span>{item.conviction_score}</span>
                    <span>{item.risk_flags?.join(', ') || 'NONE'}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="portfolio-card">
              <h4>Diversification</h4>
              <div className="breakdown-list">
                {Object.entries(sectorBreakdown).map(([key, value]) => (
                  <div key={key} className="breakdown-row">
                    <span>{key}</span>
                    <span>{value}%</span>
                  </div>
                ))}
              </div>
              <h5>Factor Exposure</h5>
              <div className="breakdown-list">
                {Object.entries(factorBreakdown).map(([key, value]) => (
                  <div key={key} className="breakdown-row">
                    <span>{key}</span>
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="portfolio-card">
              <h4>Risk and Resilience</h4>
              <div className="breakdown-list">
                <div className="breakdown-row">
                  <span>Regime Gate</span>
                  <span>{risk?.regime_gate_state || holdings?.regime_gate_state}</span>
                </div>
                <div className="breakdown-row">
                  <span>Concentration Score</span>
                  <span>{risk?.risk?.concentration_score}</span>
                </div>
                <div className="breakdown-row">
                  <span>Macro Sensitivity</span>
                  <span>{risk?.risk?.macro_sensitivity}</span>
                </div>
                <div className="breakdown-row">
                  <span>Resilience</span>
                  <span>{resilience?.resilience?.overall_score} {resilience?.resilience?.classification}</span>
                </div>
              </div>
            </div>

            <div className="portfolio-card">
              <h4>Source and Diagnostics</h4>
              <div className="breakdown-list">
                <div className="breakdown-row">
                  <span>Portfolio Data Source</span>
                  <span className={`source-badge source-${portfolioDataSource.toLowerCase()}`}>{portfolioDataSource}</span>
                </div>
                <div className="breakdown-row">
                  <span>Broker Connectivity</span>
                  <span>{diagnostics?.broker_connectivity || 'UNAVAILABLE'}</span>
                </div>
                <div className="breakdown-row">
                  <span>MCP Status</span>
                  <span>{mcpDiagnostics?.portfolio_fetch_status || mcpDiagnostics?.connectivity_status || 'UNAVAILABLE'}</span>
                </div>
                <div className="breakdown-row">
                  <span>API Fallback</span>
                  <span>{apiFallback?.status || 'UNAVAILABLE'}</span>
                </div>
                <div className="breakdown-row">
                  <span>Refresh Timestamp</span>
                  <span>{holdings?.portfolio_refresh_timestamp || selectedPortfolio?.portfolio_refresh_timestamp || 'UNAVAILABLE'}</span>
                </div>
              </div>
            </div>

            <div className="portfolio-card">
              <h4>Insights</h4>
              <div className="insight-list">
                {insightRows.map((item, index) => (
                  <div className={`insight-item ${item.severity?.toLowerCase() || 'info'}`} key={`${item.category}-${index}`}>
                    <strong>{item.headline}</strong>
                    <span>{item.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="portfolio-combined-bar">
            <span>Combined US Value: {combined?.us_portfolio_value ?? 0}</span>
            <span>Combined India Value: {combined?.india_portfolio_value ?? 0}</span>
            <span>Combined USD: {combined?.combined_value_usd ?? 'BLOCKED'}</span>
            <span>FX Source: {combined?.fx_source}</span>
          </div>
        </>
      )}
    </section>
  );
};

export default PortfolioIntelligencePanel;
