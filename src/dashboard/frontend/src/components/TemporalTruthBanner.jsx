import React, { useEffect, useState } from "react";
import api from "../services/api";
import "./TemporalTruthBanner.css";

/**
 * TemporalTruthBanner
 * Displays TE/CTT/RDT state with bounded-drift governance signals.
 */
export default function TemporalTruthBanner({ market = "US" }) {
  const [temporalState, setTemporalState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTemporalStatus = async () => {
      try {
        const response = await api.get(`/intelligence/temporal/status?market=${market}`);
        setTemporalState(response.data);
        setError(null);
      } catch (err) {
        setError("Failed to load temporal status");
        console.error("Temporal API Error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTemporalStatus();
    const interval = setInterval(fetchTemporalStatus, 60000);
    return () => clearInterval(interval);
  }, [market]);

  if (loading) {
    return <div className="temporal-banner loading">Loading temporal state...</div>;
  }

  if (error || !temporalState || temporalState.error) {
    return <div className="temporal-banner error">TEMPORAL STATE UNAVAILABLE</div>;
  }

  const ts = temporalState.temporal_state || {};
  const drift = temporalState.drift_status || {};
  const holds = temporalState.holds || {};
  const governancePause = temporalState.governance_pause || {};
  const evalWindow = temporalState.evaluation_window;

  const driftDays = Number(drift.evaluation_drift_days || 0);
  const maxDrift = Number(drift.max_drift_days || 7);
  const limitExceeded =
    drift.drift_limit_exceeded === true || drift.status_code === "DRIFT_LIMIT_EXCEEDED";

  let statusClass = "sync";
  if (drift.status_code === "CRITICAL_FUTURE_LEAKAGE") statusClass = "critical";
  else if (limitExceeded) statusClass = "exceeded";
  else if (drift.status_code === "EVALUATION_PENDING") statusClass = "pending";

  const statusText = limitExceeded
    ? "EVAL REQUIRED - DRIFT WINDOW EXCEEDED"
    : drift.status_code || "UNKNOWN";

  return (
    <div className={`temporal-banner ${statusClass}`}>
      <div className="temporal-row">
        <div className="temporal-segment epoch">
          <span className="label">TRUTH EPOCH (TE)</span>
          <span className="value">{ts.truth_epoch?.timestamp || "N/A"}</span>
          {ts.truth_epoch?.status === "FROZEN" && <span className="badge frozen">FROZEN</span>}
        </div>

        <div className="temporal-segment ctt">
          <span className="label">CANONICAL (CTT)</span>
          <span className="value">{ts.canonical_truth_time?.timestamp || "N/A"}</span>
        </div>

        <div className="temporal-segment rdt">
          <span className="label">RAW DATA (RDT)</span>
          <span className="value">{ts.raw_data_time?.timestamp || "N/A"}</span>
        </div>

        <div className="temporal-segment drift">
          <span className="badge status-badge">{statusText}</span>
          <span className="drift-metric">
            Drift: {driftDays}d | Max: {maxDrift}d
          </span>
          {limitExceeded && <span className="badge exceeded-badge">DRIFT_LIMIT_EXCEEDED</span>}
        </div>
      </div>

      <div className="temporal-detail-row">
        <div className="detail-block">
          <span className="detail-label">WHY BLOCKED</span>
          <span className="detail-value">
            {drift.human_explanation || drift.message || "No explanation available."}
          </span>
        </div>
        <div className="detail-block">
          <span className="detail-label">REQUIRED OPERATOR ACTION</span>
          <span className="detail-value">
            {drift.required_operator_action ||
              governancePause.required_operator_action ||
              "No action required"}
          </span>
        </div>
        <div className="detail-block">
          <span className="detail-label">EVALUATION HOLD</span>
          <span className="detail-value">
            {holds.evaluation_hold ? `ACTIVE - ${holds.reason || "Hold active"}` : "INACTIVE"}
          </span>
        </div>
      </div>

      {evalWindow && (
        <div className="window-row">
          <span className="window-label">REQUESTED WINDOW</span>
          <span className="window-value">
            {evalWindow.window_start} to {evalWindow.window_end}
          </span>
          <span className="badge window-badge">{evalWindow.status || "REQUESTED"}</span>
        </div>
      )}
    </div>
  );
}
