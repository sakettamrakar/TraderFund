import React, { useEffect, useMemo, useState } from 'react';

const StockResearchPanel = ({ profiles = [], summaries = [] }) => {
  const sortedProfiles = useMemo(
    () => [...profiles].sort((a, b) => (b.portfolio_weight || 0) - (a.portfolio_weight || 0)),
    [profiles],
  );
  const [selectedTicker, setSelectedTicker] = useState(sortedProfiles[0]?.ticker || null);

  useEffect(() => {
    setSelectedTicker(sortedProfiles[0]?.ticker || null);
  }, [sortedProfiles]);

  const effectiveTicker = selectedTicker || sortedProfiles[0]?.ticker || null;
  const selectedProfile = sortedProfiles.find((item) => item.ticker === effectiveTicker) || sortedProfiles[0] || null;
  const selectedSummary = summaries.find((item) => item.ticker === effectiveTicker) || null;

  if (!selectedProfile) {
    return (
      <div className="portfolio-card intelligence-panel">
        <h4>Stock Research Profiles</h4>
        <div className="insight-item info">
          <strong>No stock research available</strong>
          <span>Research engine output is unavailable for this portfolio.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolio-card intelligence-panel stock-research-panel">
      <h4>Stock Research Profiles</h4>
      <div className="research-chip-row">
        {sortedProfiles.slice(0, 10).map((profile) => (
          <button
            key={profile.ticker}
            className={`research-chip ${profile.ticker === effectiveTicker ? 'active' : ''}`}
            onClick={() => setSelectedTicker(profile.ticker)}
          >
            {profile.ticker} ({profile.portfolio_weight.toFixed(1)}%)
          </button>
        ))}
      </div>

      <div className="research-grid">
        <div className="research-block">
          <h5>{selectedProfile.ticker} Intelligence</h5>
          <div className="research-row"><span>Portfolio Role</span><strong>{selectedProfile.portfolio_role}</strong></div>
          <div className="research-row"><span>Role Category</span><strong>{selectedProfile.portfolio_role_category}</strong></div>
          <div className="research-row"><span>Confidence</span><strong>{selectedProfile.confidence_level}</strong></div>
          <div className="research-row"><span>Monitoring Status</span><strong>{selectedProfile.monitoring_status || 'NO_ACTIVE_EVENT'}</strong></div>
          <div className="research-row"><span>Valuation Status</span><strong>{selectedProfile.valuation_status}</strong></div>
          <div className="research-row"><span>Macro Alignment</span><strong>{selectedProfile.macro_regime_alignment?.score}</strong></div>
          <div className="research-row"><span>Macro Sensitivity</span><strong>{selectedProfile.macro_sensitivity}</strong></div>
        </div>
        <div className="research-block">
          <h5>Fundamental View</h5>
          <p>{selectedProfile.fundamental_summary}</p>
          <p>{selectedProfile.fundamental_outlook}</p>
          <p>{selectedProfile.growth_outlook}</p>
          <p>{selectedProfile.profitability_profile}</p>
          <p>{selectedProfile.balance_sheet_strength}</p>
        </div>
        <div className="research-block">
          <h5>Valuation View</h5>
          <p>{selectedProfile.valuation_analysis?.summary}</p>
          <p>Relative valuation: {selectedProfile.relative_valuation}</p>
          <p>
            Intrinsic estimate: {selectedProfile.intrinsic_value_estimate?.fair_multiple ?? 'UNAVAILABLE'}
            {' '}({selectedProfile.intrinsic_value_estimate?.method || 'N/A'})
          </p>
        </div>
        <div className="research-block">
          <h5>Technical and Risk View</h5>
          <p>{selectedProfile.technical_structure?.summary}</p>
          <p>Technical trend: {selectedProfile.technical_trend}</p>
          <p>Trend strength: {selectedProfile.trend_strength}</p>
          <p>Volatility profile: {selectedProfile.volatility_profile}</p>
          <p>Primary macro takeaway: {selectedProfile.macro_regime_alignment?.summary}</p>
        </div>
      </div>

      {selectedSummary && (
        <div className="research-narrative-block">
          <strong>Stock Intelligence Summary</strong>
          <span>{selectedSummary.summary}</span>
          <em>{selectedProfile.research_narrative}</em>
        </div>
      )}

      {selectedProfile.event_intelligence?.events?.length > 0 && (
        <div className="research-narrative-block">
          <strong>Event Timeline</strong>
          {selectedProfile.event_intelligence.events.slice(0, 4).map((event, index) => (
            <span key={`${event.headline}-${index}`}>
              {event.published_at} | {event.headline} | {event.risk_level}
            </span>
          ))}
          <em>{selectedProfile.narrative_summary}</em>
        </div>
      )}

      <div className="research-risk-flags">
        <h5>Opportunity Signals</h5>
        {selectedProfile.opportunity_signals?.length ? selectedProfile.opportunity_signals.map((signal, index) => (
          <div className="research-flag research-flag-opportunity" key={`${signal.signal}-${index}`}>
            <strong>{signal.signal.replace(/_/g, ' ')}</strong>
            <span>{signal.explanation}</span>
            <em>Confidence: {signal.confidence_level}</em>
          </div>
        )) : <span className="research-empty">No current opportunity signals.</span>}
      </div>

      <div className="research-risk-flags">
        <h5>Risk Flags</h5>
        {selectedProfile.risk_flags?.length ? selectedProfile.risk_flags.map((flag, index) => (
          <div className="research-flag" key={`${flag.flag}-${index}`}>
            <strong>{flag.flag.replace(/_/g, ' ')}</strong>
            <span>{flag.explanation}</span>
            <em>Confidence: {flag.confidence_level}</em>
          </div>
        )) : <span className="research-empty">No active stock-level risk flags.</span>}
      </div>
    </div>
  );
};

export default StockResearchPanel;