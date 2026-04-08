import React from 'react';

const LookthroughCoveragePanel = ({ funds = [] }) => {
  const rows = [...funds].sort((a, b) => (b.weight_pct || 0) - (a.weight_pct || 0));

  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Look-through Coverage</h4>
      <div className="portfolio-table">
        <div className="portfolio-table-header lookthrough-coverage-header">
          <span>Fund</span>
          <span>Mode</span>
          <span>Benchmark</span>
          <span>Source</span>
        </div>
        {rows.length === 0 && (
          <div className="portfolio-table-row lookthrough-coverage-row">
            <span>None</span>
            <span>-</span>
            <span>-</span>
            <span>-</span>
          </div>
        )}
        {rows.map((fund) => (
          <div className="portfolio-table-row lookthrough-coverage-row" key={fund.ticker}>
            <span>{fund.security_name || fund.ticker}</span>
            <span>{fund.lookthrough_mode || 'UNAVAILABLE'}</span>
            <span>{fund.benchmark_reference || 'UNMAPPED'}</span>
            <span>{fund.lookthrough_provenance?.metadata_source || fund.metadata_source || 'UNAVAILABLE'}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LookthroughCoveragePanel;