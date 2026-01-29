import React, { useState } from 'react';
import SystemStatus from './components/SystemStatus';
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
import './App.css';

function App() {
  const [lastRefreshed, setLastRefreshed] = useState(new Date());
  const [selectedMarket, setSelectedMarket] = useState("US");

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="dashboard-container">
      <div className="market-selector-bar" style={{ padding: '10px 20px', background: '#111', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <span style={{ color: '#888', alignSelf: 'center' }}>MARKET VIEW:</span>
          <button
              onClick={() => setSelectedMarket("US")}
              style={{
                  background: selectedMarket === "US" ? '#2196F3' : '#333',
                  color: '#fff', border: 'none', padding: '5px 15px', cursor: 'pointer', borderRadius: '4px'
              }}>
              US (Core)
          </button>
          <button
              onClick={() => setSelectedMarket("IN")}
              style={{
                  background: selectedMarket === "IN" ? '#FF9800' : '#333',
                  color: '#fff', border: 'none', padding: '5px 15px', cursor: 'pointer', borderRadius: '4px'
              }}>
              INDIA (Adapter)
          </button>
      </div>

      <SystemStatus market={selectedMarket} />

      <SystemNarrative />

      <div className="main-content">
        <div className="left-panel">
          <MacroContextPanel market={selectedMarket} />
          <WhyNothingIsHappening />
          <CapitalStoryPanel />
          <LayerHealth />
          <MarketSnapshot market={selectedMarket} />
          <WatcherTimeline />
        </div>

        <div className="right-panel">
          <CapitalReadinessPanel />
          <StrategyMatrix market={selectedMarket} />
          <CapitalInvariants />
          <ChangeConditions />
        </div>
      </div>

      <div className="footer-system-posture">
        <div className="posture-disclaimer">
          <strong>SYSTEM POSTURE:</strong> Intentional Inactivity. All execution hooks are disabled. The system is operating in Observer-Only mode to protect equity until structural edge is confirmed by Strategy Evolution v1 rules.
        </div>
        <div className="footer-meta">
          <span>TraderFund Market Intelligence Dashboard (Observer Only)</span>
          <button onClick={handleRefresh} className="refresh-btn">
            REFRESH DATA (Last: {lastRefreshed.toLocaleTimeString()})
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
