import { useState, useEffect } from 'react';
import { getMarketParity } from '../services/api';
import './DataAnchorPanel.css';

/**
 * DataAnchorPanel - EPISTEMIC RESTORATION LAYER
 * Displays Data Scale and Coverage (A1.1 / A3.2)
 */
const DataAnchorPanel = ({ market = "US" }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        getMarketParity(market)
            .then(res => {
                setData(res);
                setLoading(false);
            })
            .catch(err => {
                console.error("DataAnchor Error:", err);
                setError(err.message);
                setLoading(false);
            });
    }, [market]);

    if (loading) return <div className="data-anchor-panel loading">Quantifying Data Scale...</div>;
    if (error) return <div className="data-anchor-panel error">Governance Binding Failure: {error}</div>;
    if (!data?.parity) return <div className="data-anchor-panel empty">No Parity Data Registered</div>;

    const { parity, trace } = data;
    const diagnostics = Object.entries(parity?.proxy_diagnostics || {});

    return (
        <div className="data-anchor-panel">
            <div className="anchor-header">
                <div className="epoch-badge">
                    <span className="epoch-label">Truth Epoch</span>
                    <span className="epoch-id">{data?.truth_epoch?.epoch_id || "TE-2026-02-07"}</span>
                </div>
                <div className="market-badge">
                    <span className="market-label">Market Sector:</span>
                    <span className="market-id">{parity?.market}</span>
                </div>
                <div className="mechanical-tag">READ-ONLY MECHANICAL TRACE</div>
            </div>

            <div className="anchor-grid">
                {diagnostics.map(([role, diagnostic]) => (
                    <div key={role} className="anchor-card">
                        <div className="role-header">
                            <span className="role-id">A3.2</span>
                            <h4>{role.replace('_', ' ').toUpperCase()}</h4>
                        </div>
                        <div className="stat-value">{diagnostic?.symbol}</div>
                        <div className="stat-detail">
                            Available: {diagnostic?.rows} | Required: {diagnostic?.required || (role === 'rates_anchor' ? 60 : 200)}
                        </div>
                        <div className="stat-provenance">Origin: {diagnostic?.source || diagnostic?.provenance}</div>
                        <div className={`status-tag-mini ${diagnostic?.status?.toLowerCase()}`}>
                            STATE: {diagnostic?.status}
                        </div>
                    </div>
                ))}
            </div>

            <div className="trace-footer">
                <div className="trace-badge">
                    A1.1 | Source Artifact: {trace?.source} | Generation: {data?.truth_epoch?.epoch_id || "TE-2026-02-07"}
                </div>
                <div className="disclaimer-mini">
                    Measurements reflect Truth Epoch {data?.truth_epoch?.epoch_id || "TE-2026-02-07"} and do not imply future sufficiency or intent.
                </div>
            </div>
        </div>
    );
};

export default DataAnchorPanel;
