import React from 'react';

const MutualFundIntelligencePanel = ({ intelligence = {} }) => {
  const profiles = intelligence.fund_profiles || [];
  const insights = intelligence.insights || [];
  const topNarratives = intelligence.top_fund_narratives || [];
  const allocationMix = intelligence.allocation_mix || {};

  return (
    <div className="portfolio-card intelligence-panel">
      <h4>Mutual Fund Intelligence</h4>
      <div className="research-narrative-block">
        <strong>Fund Sleeve Summary</strong>
        <span>{intelligence.summary || 'No mutual fund allocation intelligence available.'}</span>
      </div>

      <h5>Allocation Mix</h5>
      <div className="breakdown-list">
        {Object.entries(allocationMix).length === 0 && (
          <div className="breakdown-row">
            <span>None</span>
            <span>0%</span>
          </div>
        )}
        {Object.entries(allocationMix).map(([key, value]) => (
          <div className="breakdown-row" key={key}>
            <span>{key}</span>
            <span>{value}%</span>
          </div>
        ))}
      </div>

      <h5>Fund Insights</h5>
      <div className="insight-list">
        {insights.length === 0 && (
          <div className="insight-item info">
            <strong>No dominant fund sleeve risks</strong>
            <span>Current mutual fund allocation does not trigger an additional advisory signal.</span>
          </div>
        )}
        {insights.map((item, index) => (
          <div className="insight-item info" key={`${item.category}-${index}`}>
            <strong>{item.headline}</strong>
            <span>{item.detail}</span>
          </div>
        ))}
      </div>

      {profiles.length > 0 && (
        <>
          <h5>Fund Profiles</h5>
          <div className="fund-profile-list">
            {profiles.slice(0, 5).map((profile) => (
              <div className="fund-profile-card" key={profile.ticker}>
                <div className="fund-profile-header">
                  <strong>{profile.security_name}</strong>
                  <span>{profile.portfolio_weight}%</span>
                </div>
                <div className="fund-profile-meta">
                  <span>{profile.portfolio_role}</span>
                  <span>{profile.fund_category}</span>
                  <span>{profile.strategy_type}</span>
                  <span>Risk: {profile.risk_level}</span>
                </div>
                <p>{profile.narrative}</p>
                {profile.risk_flags?.length > 0 && (
                  <div className="fund-profile-flags">
                    {profile.risk_flags.map((flag, index) => (
                      <div className="research-flag" key={`${profile.ticker}-risk-${index}`}>
                        <strong>{flag.flag.replace(/_/g, ' ')}</strong>
                        <span>{flag.explanation}</span>
                      </div>
                    ))}
                  </div>
                )}
                {profile.opportunity_signals?.length > 0 && (
                  <div className="fund-profile-flags">
                    {profile.opportunity_signals.map((signal, index) => (
                      <div className="research-flag research-flag-opportunity" key={`${profile.ticker}-opp-${index}`}>
                        <strong>{signal.signal.replace(/_/g, ' ')}</strong>
                        <span>{signal.explanation}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}

      {topNarratives.length > 0 && (
        <div className="research-risk-flags">
          <h5>Top Fund Narratives</h5>
          {topNarratives.map((item) => (
            <div className="research-flag research-flag-opportunity" key={item.ticker}>
              <strong>{item.security_name}</strong>
              <span>{item.narrative}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MutualFundIntelligencePanel;