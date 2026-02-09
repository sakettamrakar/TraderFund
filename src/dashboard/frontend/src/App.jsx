import React, { useState, useEffect } from 'react';
import { getEvaluationScope } from './services/api';
import { useInspection } from './context/InspectionContext';
import SystemStatus from './components/SystemStatus';
import SystemPosture from './components/SystemPosture';
import LayerHealth from './components/LayerHealth';
import MarketSnapshot from './components/MarketSnapshot';
import WatcherTimeline from './components/WatcherTimeline';
import StrategyMatrix from './components/StrategyMatrix';
import ChangeConditions from './components/ChangeConditions';
import SystemNarrative from './components/SystemNarrative';
import WhyNothingIsHappening from './components/WhyNothingIsHappening';
import CapitalReadinessPanel from './components/CapitalReadinessPanel';
import CapitalStoryPanel from './components/CapitalStoryPanel';
import CapitalInvariants from './components/CapitalInvariants';
import MacroContextPanel from './components/MacroContextPanel';
import IntelligencePanel from './components/IntelligencePanel';
import DataAnchorPanel from './components/DataAnchorPanel';
import TemporalTruthBanner from './components/TemporalTruthBanner';
import './components/GlobalHeader.css';
import './App.css';

function App() {
  const [lastRefreshed, setLastRefreshed] = useState(new Date());
  const [market, setMarket] = useState('US');
  const [scopeData, setScopeData] = useState(null);
  const { isInspectionMode } = useInspection();

  useEffect(() => {
    getEvaluationScope()
      .then(data => {
        setScopeData(data);
        // If current market not in scope, but something else is, maybe switch? 
        // For now, just track scope.
      })
      .catch(console.error);
  }, []);

  const handleRefresh = () => {
    window.location.reload();
  };

  const inScopeMarkets = scopeData?.scope?.evaluated_markets || [];

  return (
    <div className={`dashboard-container ${isInspectionMode ? 'inspection-mode-active' : ''}`}>
      {isInspectionMode && (
        <div className="inspection-banner">
          ⚠️ INSPECTION MODE — SCENARIO VISUALIZATION ONLY — NOT LIVE TRUTH ⚠️
        </div>
      )}
      <TemporalTruthBanner market={market} />
      <SystemStatus market={market} />
      <SystemPosture />


      <SystemNarrative market={market} />

      <div className="main-content">
        <div className="left-panel">
          <div className="panel-header-controls">
            <div className="market-scope-group">
              <span className="control-label">MARKET SCOPE (EVALUATED):</span>
              <div className="market-selector-global">
                <button
                  className={`${market === 'US' ? 'active' : ''} ${!inScopeMarkets.includes('US') ? 'out-of-scope' : ''}`}
                  onClick={() => setMarket('US')}
                  disabled={!inScopeMarkets.includes('US')}
                >
                  US {!inScopeMarkets.includes('US') && '(OUT)'}
                </button>
                <button
                  className={`${market === 'INDIA' ? 'active' : ''} ${!inScopeMarkets.includes('INDIA') ? 'out-of-scope' : ''}`}
                  onClick={() => setMarket('INDIA')}
                  disabled={!inScopeMarkets.includes('INDIA')}
                >
                  INDIA {!inScopeMarkets.includes('INDIA') && '(OUT)'}
                </button>
              </div>
              <div className="trace-badge mini">
                Source: {scopeData?.trace?.source} | Epoch: {scopeData?.scope?.last_evaluation_epoch || 'N/A'}
              </div>
            </div>
          </div>

          {/* EPISTEMIC RESTORATION: Data Anchor Panel - Shows above all content */}
          <DataAnchorPanel market={market} />

          <MacroContextPanel market={market} />
          <IntelligencePanel market={market} />
          <WhyNothingIsHappening market={market} />
          <CapitalStoryPanel market={market} />
          <LayerHealth market={market} />
          <MarketSnapshot market={market} />
          <WatcherTimeline market={market} />
        </div>

        <div className="right-panel">
          <CapitalReadinessPanel market={market} />
          <StrategyMatrix market={market} />
          <CapitalInvariants market={market} />
          <ChangeConditions market={market} />
        </div>
      </div>

      <div className="footer-system-posture">
        <div className="posture-disclaimer">
          <strong>SYSTEM POSTURE:</strong> {isInspectionMode ?
            "SIMULATED: Inspection Mode active. All data shown is hypothetical." :
            "Intentional Inactivity. All execution hooks are recorded as DISABLED for the current frozen Truth Epoch. The system is operating in Observer-Only mode to protect equity. This state does not imply future activation."}
        </div>
        <div className="footer-meta">
          <span>TraderFund Market Intelligence Dashboard (Observer Only) [{market}]</span>
          <span className="resolution-tag">Resolution: DAILY (End of Day)</span>
          <button onClick={handleRefresh} className="refresh-btn">
            REFRESH DATA (Last: {lastRefreshed.toLocaleTimeString()})
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
