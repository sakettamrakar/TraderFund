import React from 'react';

const ValuationOverviewPanel = ({ valuationOverview = {} }) => {
  const counts = valuationOverview.counts || {};
  const undervalued = valuationOverview.undervalued || [];
  const fairlyValued = valuationOverview.fairly_valued || [];
  const overvalued = valuationOverview.overvalued || [];

  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Valuation Overview</h4>
      <div className="valuation-grid">
        <div className="valuation-pill undervalued">
          <span>Undervalued</span>
          <strong>{counts.undervalued || 0}</strong>
        </div>
        <div className="valuation-pill fairly-valued">
          <span>Fairly Valued</span>
          <strong>{counts.fairly_valued || 0}</strong>
        </div>
        <div className="valuation-pill overvalued">
          <span>Overvalued</span>
          <strong>{counts.overvalued || 0}</strong>
        </div>
      </div>
      <div className="valuation-lists">
        <div>
          <h5>Undervalued</h5>
          <span>{undervalued.length ? undervalued.join(', ') : 'NONE'}</span>
        </div>
        <div>
          <h5>Fairly Valued</h5>
          <span>{fairlyValued.length ? fairlyValued.join(', ') : 'NONE'}</span>
        </div>
        <div>
          <h5>Overvalued</h5>
          <span>{overvalued.length ? overvalued.join(', ') : 'NONE'}</span>
        </div>
      </div>
    </div>
  );
};

export default ValuationOverviewPanel;