import React from 'react';

const PortfolioEventIntelligencePanel = ({ adapterStatus = {}, alerts = [], timeline = [] }) => {
  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Portfolio Event Intelligence</h4>
      <div className="breakdown-list">
        <div className="breakdown-row"><span>Adapter Status</span><span>{adapterStatus.status || 'UNAVAILABLE'}</span></div>
        <div className="breakdown-row"><span>Adapter Source</span><span>{adapterStatus.source || 'UNAVAILABLE'}</span></div>
        <div className="breakdown-row"><span>Story Count</span><span>{adapterStatus.story_count ?? 0}</span></div>
      </div>

      <h5>Portfolio Event Alerts</h5>
      <div className="insight-list">
        {alerts.length === 0 && (
          <div className="insight-item info">
            <strong>No active portfolio event alerts</strong>
            <span>No portfolio-relevant news events are currently linked, or the news source is unavailable.</span>
          </div>
        )}
        {alerts.slice(0, 6).map((alert, index) => (
          <div className="insight-item orange" key={`${alert.ticker}-${index}`}>
            <strong>{alert.ticker} | {alert.headline}</strong>
            <span>{alert.potential_risk_implications}</span>
            <em>{alert.monitoring_recommendation}</em>
          </div>
        ))}
      </div>

      <h5>Event Timeline</h5>
      <div className="portfolio-table">
        <div className="portfolio-table-header portfolio-trend-header">
          <span>Time</span>
          <span>Ticker</span>
          <span>Risk</span>
          <span>Source</span>
        </div>
        {timeline.slice(0, 6).map((event, index) => (
          <div className="portfolio-table-row portfolio-trend-row" key={`${event.ticker}-${event.headline}-${index}`}>
            <span>{event.published_at}</span>
            <span>{event.ticker}</span>
            <span>{event.risk_level}</span>
            <span>{event.source}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PortfolioEventIntelligencePanel;