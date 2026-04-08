import React from 'react';

const PortfolioSuggestionsPanel = ({ suggestions = [], synthesis = {} }) => {
  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Portfolio Strategy Suggestions</h4>
      {synthesis?.portfolio_narrative && (
        <div className="research-narrative-block">
          <strong>Prescriptive Intelligence Narrative</strong>
          <span>{synthesis.portfolio_narrative}</span>
          <em>{synthesis.research_style_summary}</em>
        </div>
      )}
      <div className="insight-list">
        {suggestions.length === 0 && (
          <div className="insight-item info">
            <strong>No dominant advisory signal</strong>
            <span>Current portfolio suggestions are neutral. This remains advisory only.</span>
          </div>
        )}
        {suggestions.map((item, index) => (
          <div className="insight-item info" key={`${item.category}-${index}`}>
            <strong>{item.headline}</strong>
            <span>{item.detail}</span>
            <em>{item.category} · Confidence: {item.confidence_level}</em>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PortfolioSuggestionsPanel;