# Active Constraints

## Data Source Limitations
*   **Alpha Vantage (US)**: Restricted by API call limits (standard tier). Requires strict batching and polling limits.
*   **Angel One (India)**: WebSocket reliance. Connection stability is critical; data gaps must be handled/backfilled explicitly.
*   **Rate Limits**: All ingestion must respect 3rd party rate limits (hard constraint).

## Infrastructure & Latency
*   **Local Execution**: Currently running on local hardware/Docker.
*   **Latency Tolerance**: The system is designed for **Intraday Momentum** (1-minute candles), not HFT. Latency of seconds is acceptable; milliseconds are not required.

## Capital & Execution
*   **Capital**: $0 (Paper/Research only). No real capital at risk.
*   **Execution**: Simulated/Paper execution only. No real broker connectivity for orders.

## Cognitive Bandwidth Constraint
Operator attention is a scarce and finite resource. The system treats excessive signal or narrative generation as a critical failure state. Genesis thresholds and caps are operational limits to prevent cognitive flooding, not just performance tunables.

## Operational
*   **Manpower**: Limited to core maintainer. Automation is key for scale. "Human-in-the-loop" is required for critical validation (Clinical Review) but must be minimized for operations.
