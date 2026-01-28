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

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="dashboard-container">
      <SystemStatus />

      <SystemNarrative />

      <div className="main-content">
        <div className="left-panel">
          <MacroContextPanel />
          <WhyNothingIsHappening />
          <CapitalStoryPanel />
          <LayerHealth />
          <MarketSnapshot />
          <WatcherTimeline />
        </div>

        <div className="right-panel">
          <CapitalReadinessPanel />
          <StrategyMatrix />
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
