import React from 'react';

const PortfolioStrategySummaryPanel = ({ summary = {}, strengtheningInsights = [] }) => {
  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Portfolio Intelligence Summary</h4>
      <div className="research-narrative-block">
        <strong>Resilience Assessment</strong>
        <span>{summary.resilience_assessment || 'Strategy summary unavailable.'}</span>
      </div>
      <div className="breakdown-list">
        <div className="breakdown-row strategy-summary-row">
          <span>Sector Concentration</span>
          <span>{summary.sector_concentration_analysis || 'UNAVAILABLE'}</span>
        </div>
        <div className="breakdown-row strategy-summary-row">
          <span>Macro Compatibility</span>
          <span>{summary.macro_regime_compatibility || 'UNAVAILABLE'}</span>
        </div>
        <div className="breakdown-row strategy-summary-row">
          <span>Factor Imbalance</span>
          <span>{summary.factor_imbalance_detection || 'UNAVAILABLE'}</span>
        </div>
        <div className="breakdown-row strategy-summary-row">
          <span>Mutual Fund Sleeve</span>
          <span>{summary.mutual_fund_sleeve_assessment || 'UNAVAILABLE'}</span>
        </div>
      </div>
      {strengtheningInsights.length > 0 && (
        <div className="research-risk-flags">
          <h5>Portfolio Strengthening Insights</h5>
          {strengtheningInsights.map((item, index) => (
            <div className="research-flag" key={`strength-${index}`}>
              <span>{item}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PortfolioStrategySummaryPanel;