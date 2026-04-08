import React from 'react';

const OpportunitySignalsPanel = ({ signals = [] }) => {
  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Opportunity Signals</h4>
      <div className="insight-list">
        {signals.length === 0 && (
          <div className="insight-item info">
            <strong>No current opportunity emphasis</strong>
            <span>Research engine did not detect a dominant stock-level opportunity cluster.</span>
          </div>
        )}
        {signals.map((item, index) => (
          <div className="insight-item info" key={`${item.ticker}-${item.signal}-${index}`}>
            <strong>{item.ticker}: {item.signal.replace(/_/g, ' ')}</strong>
            <span>{item.explanation}</span>
            <em>{item.portfolio_role} · Confidence: {item.confidence_level}</em>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OpportunitySignalsPanel;