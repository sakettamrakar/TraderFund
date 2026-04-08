import React, { useState } from 'react';

const SEVERITY_CLASS = {
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

const EXPOSURE_METRIC_DEFS = {
  diversification: {
    label: 'Diversification',
    short: 'Spread of holdings across sectors — 1.0 = perfectly diversified.',
    guide: 'Based on Herfindahl-Hirschman Index (HHI) of sector weights.',
  },
  concentration: {
    label: 'Concentration',
    short: 'Inverse of top-3 position weight concentration.',
    guide: 'Lower = more concentrated in few positions.',
  },
  factorBalance: {
    label: 'Factor Balance',
    short: 'Evenness of factor exposure across growth, value, momentum, quality.',
    guide: 'Higher = more balanced. Low value = single-factor dominance.',
  },
  regimeAlignment: {
    label: 'Regime Alignment',
    short: 'How well portfolio tilt matches current macro regime.',
    guide: 'Higher = portfolio positioned for current conditions.',
  },
  compositeHealth: {
    label: 'Composite Health',
    short: 'Average of diversification, concentration, factor, regime scores.',
    guide: '> 0.7 strong · 0.4–0.7 adequate · < 0.4 fragile',
  },
  correlatedClusters: {
    label: 'Correlated Risk Clusters',
    short: 'Holdings that move together due to sector or factor correlation.',
    guide: 'More clusters = higher hidden concentration risk.',
  },
  regimeVulnerability: {
    label: 'Regime Vulnerability',
    short: 'Portfolio exposures that could suffer under current macro regime.',
    guide: 'Flags indicate positional risks given current regime state.',
  },
};

const ExposureTooltip = ({ defKey }) => {
  const [open, setOpen] = useState(false);
  const def = EXPOSURE_METRIC_DEFS[defKey];
  if (!def) return null;
  return (
    <span
      className="metric-tooltip-trigger"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      ⓘ
      {open && (
        <span className="metric-tooltip-popup">
          <strong>{def.label}</strong>
          <span>{def.short}</span>
          <em>{def.guide}</em>
        </span>
      )}
    </span>
  );
};

const Bar = ({ value, max = 100, label }) => {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  return (
    <div className="exposure-bar-row">
      <span className="exposure-bar-label">{label}</span>
      <div className="exposure-bar-track">
        <div className="exposure-bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="exposure-bar-value">{typeof value === 'number' ? value.toFixed(2) : value}</span>
    </div>
  );
};

const ScoreCard = ({ label, value, classification, defKey }) => {
  const status = value >= 0.7 ? 'strong' : value >= 0.4 ? 'adequate' : 'fragile';
  return (
    <div className="exposure-score-card">
      <span className="score-label">{label} {defKey && <ExposureTooltip defKey={defKey} />}</span>
      <strong className={`score-value score-${status}`}>{typeof value === 'number' ? value.toFixed(4) : value}</strong>
      {classification && <span className="score-class">{classification}</span>}
      <em className="score-status">{status}</em>
    </div>
  );
};

const PortfolioExposurePanel = ({ exposure, macroAlignment, metricDefs }) => {
  if (!exposure) return null;

  const sectorAlloc = exposure.sector_exposure?.allocation_pct || {};
  const factorExp = exposure.factor_exposure || {};
  const geoAlloc = exposure.geography_exposure?.country_exposure_pct || {};
  const metrics = exposure.exposure_metrics || {};
  const concentrations = exposure.hidden_concentrations || {};
  const macro = macroAlignment?.macro_regime_exposure || exposure.macro_regime_exposure || {};
  const exposureInsights = exposure.exposure_insights || [];
  const clusters = concentrations.correlated_holdings_clusters || {};
  const maxSectorWeight = Math.max(...Object.values(sectorAlloc), 1);
  const lookthrough = exposure.lookthrough_summary || {};

  return (
    <div className="exposure-panel">
      <h4>Portfolio Exposure Engine</h4>

      {/* Composite Metrics */}
      <div className="exposure-scores-grid">
        <ScoreCard label="Diversification" value={metrics.diversification_score} defKey="diversification" />
        <ScoreCard label="Concentration" value={metrics.concentration_score} defKey="concentration" />
        <ScoreCard label="Factor Balance" value={metrics.factor_balance_score} defKey="factorBalance" />
        <ScoreCard label="Regime Alignment" value={metrics.regime_alignment_score} defKey="regimeAlignment" />
        <ScoreCard label="Composite Health" value={metrics.composite_health} defKey="compositeHealth" />
      </div>

      {/* Sector Exposure */}
      {(lookthrough.lookthrough_enabled || lookthrough.mutual_fund_input_count) && (
        <div className="exposure-section">
          <h5>Look-through Coverage</h5>
          <div className="breakdown-list">
            <div className="breakdown-row"><span>Fund Inputs</span><span>{lookthrough.mutual_fund_input_count ?? 0}</span></div>
            <div className="breakdown-row"><span>Real Disclosures</span><span>{lookthrough.real_disclosure_funds ?? 0}</span></div>
            <div className="breakdown-row"><span>Benchmark-linked</span><span>{lookthrough.benchmark_linked_funds ?? 0}</span></div>
            <div className="breakdown-row"><span>Fallback</span><span>{lookthrough.fallback_funds ?? 0}</span></div>
            <div className="breakdown-row"><span>Synthetic Rows</span><span>{lookthrough.synthetic_lookthrough_rows ?? 0}</span></div>
          </div>
        </div>
      )}

      {/* Sector Exposure */}
      <div className="exposure-section">
        <h5>Sector Allocation</h5>
        <div className="exposure-bars">
          {Object.entries(sectorAlloc)
            .sort(([, a], [, b]) => b - a)
            .map(([sector, weight]) => (
              <Bar key={sector} label={sector} value={weight} max={maxSectorWeight} />
            ))}
        </div>
      </div>

      {/* Factor Exposure Radar (displayed as bars) */}
      <div className="exposure-section">
        <h5>Factor Exposure</h5>
        <div className="exposure-bars">
          <Bar label="Growth" value={factorExp.growth_factor} max={1} />
          <Bar label="Value" value={factorExp.value_factor} max={1} />
          <Bar label="Momentum" value={factorExp.momentum_factor} max={1} />
          <Bar label="Quality" value={factorExp.quality_factor} max={1} />
          <Bar label="Volatility" value={factorExp.volatility_factor} max={1} />
        </div>
        <div className="exposure-tag">Dominant: {factorExp.dominant_factor}</div>
      </div>

      {/* Geography Exposure */}
      <div className="exposure-section">
        <h5>Geography Exposure</h5>
        <div className="exposure-bars">
          {Object.entries(geoAlloc)
            .sort(([, a], [, b]) => b - a)
            .map(([geo, weight]) => (
              <Bar key={geo} label={geo} value={weight} max={100} />
            ))}
        </div>
      </div>

      {/* Macro Regime Alignment */}
      <div className="exposure-section">
        <h5>Macro Regime Sensitivity</h5>
        <div className="exposure-bars">
          <Bar label="Growth Sensitivity" value={macro.growth_regime_sensitivity} max={1} />
          <Bar label="Interest Rate" value={macro.interest_rate_sensitivity} max={1} />
          <Bar label="Inflation" value={macro.inflation_sensitivity} max={1} />
          <Bar label="Liquidity" value={macro.liquidity_sensitivity} max={1} />
        </div>
        <div className="exposure-tag">
          Regime: {macro.regime_hint} &middot; Appetite: {macro.risk_appetite} &middot; Alignment: {macro.macro_alignment_score}
        </div>
        {macro.regime_vulnerability_flags?.length > 0 && (
          <div className="exposure-warnings">
            {macro.regime_vulnerability_flags.map((flag, i) => (
              <span key={i} className="exposure-warning-tag">{flag.replace(/_/g, ' ')}</span>
            ))}
          </div>
        )}
      </div>

      {/* Hidden Concentrations */}
      {concentrations.cluster_count > 0 && (
        <div className="exposure-section">
          <h5>Correlated Holdings Clusters <ExposureTooltip defKey="correlatedClusters" /></h5>
          <div className="exposure-clusters">
            {Object.entries(clusters).map(([sector, data]) => (
              <div key={sector} className="cluster-item">
                <strong>{sector}</strong>
                <span>{data.count} holdings: {data.tickers?.join(', ')}</span>
              </div>
            ))}
          </div>
          {concentrations.sector_concentration?.concentrated && (
            <div className="exposure-warning-tag">
              Sector HHI: {concentrations.sector_concentration.hhi} (CONCENTRATED)
            </div>
          )}
          {concentrations.factor_overexposure?.detected && (
            <div className="exposure-warning-tag">
              Factor overexposure: {concentrations.factor_overexposure.max_factor} ({concentrations.factor_overexposure.max_factor_value})
            </div>
          )}
        </div>
      )}

      {/* Exposure Insights */}
      {exposureInsights.length > 0 && (
        <div className="exposure-section">
          <h5>Exposure Insights</h5>
          <div className="insight-list">
            {exposureInsights.map((item, index) => (
              <div className={`insight-item ${SEVERITY_CLASS[item.severity] || 'info'}`} key={`exp-${item.category}-${index}`}>
                <strong>{item.category?.replace(/_/g, ' ')}</strong>
                <span>{item.explanation}</span>
                {item.trace?.source && <em>{item.trace.source}</em>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioExposurePanel;
