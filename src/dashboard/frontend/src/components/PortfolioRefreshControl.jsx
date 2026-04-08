import React, { useState } from 'react';

const PortfolioRefreshControl = ({ refreshStatus, onRefresh, isRefreshing }) => {
  const [headlessAuth, setHeadlessAuth] = useState(false);
  const diagnostics = refreshStatus?.refresh_diagnostics || {};
  const runtime = refreshStatus?.runtime || {};

  return (
    <div className="portfolio-refresh-control">
      <div className="portfolio-refresh-header">
        <strong>Refresh Control</strong>
        <span>{refreshStatus?.portfolio_refresh_timestamp ? `Last refresh: ${new Date(refreshStatus.portfolio_refresh_timestamp).toLocaleString()}` : 'No recorded refresh yet'}</span>
      </div>
      <div className="portfolio-refresh-meta">
        <span>Source: {refreshStatus?.portfolio_data_source || 'UNAVAILABLE'}</span>
        <span>Equities: {refreshStatus?.holding_count ?? 0}</span>
        <span>Funds: {refreshStatus?.mutual_fund_count ?? 0}</span>
      </div>
      <div className="portfolio-refresh-meta">
        <span>Broker: {diagnostics?.broker_connectivity || 'UNAVAILABLE'}</span>
        <span>MCP: {diagnostics?.mcp?.portfolio_fetch_status || diagnostics?.mcp?.connectivity_status || 'UNAVAILABLE'}</span>
        <span>API: {diagnostics?.api_fallback?.status || 'UNAVAILABLE'}</span>
      </div>
      <div className="portfolio-refresh-meta">
        <span>Runtime: {runtime?.status || 'IDLE'}</span>
        <span>Auth: {runtime?.auth_mode || diagnostics?.auth_mode || 'UNAVAILABLE'}</span>
        <span>Duration: {runtime?.last_duration_seconds ?? 'N/A'}</span>
      </div>
      <label className="portfolio-refresh-toggle">
        <input type="checkbox" checked={headlessAuth} onChange={(event) => setHeadlessAuth(event.target.checked)} />
        Use headless auth
      </label>
      <button className="portfolio-refresh-button" onClick={() => onRefresh({ headless_auth: headlessAuth })} disabled={isRefreshing}>
        {isRefreshing ? 'Refreshing...' : 'Refresh Portfolio'}
      </button>
    </div>
  );
};

export default PortfolioRefreshControl;