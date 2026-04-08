import React from 'react';

const PortfolioTrendPanel = ({ trend }) => {
  const history = trend?.history || [];
  const latest = history[history.length - 1] || null;

  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Resilience Trend</h4>
      <div className="research-narrative-block">
        <strong>Latest Drift</strong>
        <span>
          Resilience delta: {trend?.drift?.resilience_change ?? 'N/A'} | Value delta: {trend?.drift?.value_change ?? 'N/A'}
        </span>
        {latest && (
          <em>
            Latest snapshot {latest.portfolio_refresh_timestamp || latest.data_as_of} | Equity sleeve {latest.equity_sleeve_resilience ?? 'N/A'} | Fund sleeve {latest.mutual_fund_sleeve_resilience ?? 'N/A'}
          </em>
        )}
      </div>

      <div className="portfolio-table">
        <div className="portfolio-table-header portfolio-trend-header">
          <span>Snapshot</span>
          <span>Resilience</span>
          <span>Delta</span>
          <span>Fund %</span>
        </div>
        {history.length === 0 && (
          <div className="portfolio-table-row portfolio-trend-row">
            <span>No history</span>
            <span>-</span>
            <span>-</span>
            <span>-</span>
          </div>
        )}
        {history.slice(-6).reverse().map((point) => (
          <div className="portfolio-table-row portfolio-trend-row" key={point.portfolio_refresh_timestamp || point.data_as_of}>
            <span>{point.portfolio_refresh_timestamp || point.data_as_of}</span>
            <span>{point.resilience_score}</span>
            <span>{point.resilience_delta ?? 'N/A'}</span>
            <span>{point.mutual_fund_allocation_pct ?? 0}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PortfolioTrendPanel;