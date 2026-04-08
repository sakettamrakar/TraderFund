import React from 'react';

const severityClass = {
  HIGH: 'orange',
  MEDIUM: 'yellow',
  LOW: 'info',
};

const PortfolioRiskAlertsPanel = ({ alerts = [] }) => {
  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Portfolio Risk Alerts</h4>
      <div className="insight-list">
        {alerts.length === 0 && (
          <div className="insight-item info">
            <strong>No active portfolio risk alerts</strong>
            <span>Research engine did not detect a dominant portfolio-level risk requiring emphasis.</span>
          </div>
        )}
        {alerts.map((item, index) => (
          <div className={`insight-item ${severityClass[item.severity] || 'info'}`} key={`${item.flag}-${item.ticker || 'portfolio'}-${index}`}>
            <strong>{item.ticker ? `${item.ticker}: ` : ''}{item.flag.replace(/_/g, ' ')}</strong>
            <span>{item.explanation}</span>
            <em>Confidence: {item.confidence_level}</em>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PortfolioRiskAlertsPanel;