# Dashboard Alerting Rules (Read-Only)

**Principle**: Alerts inform. They never act.
**Delivery**: Dashboard UI Header (Visual Badge).
**Method**: Polling backend state (Client-side logic).

## 1. Watcher State Change (🟡 YELLOW)
**Trigger**: When a Watcher's state in the *latest* tick differs from the *previous* tick.
**Logic**:
```javascript
if (currentTick.momentum !== prevTick.momentum) {
  alert(`Momentum Changed: ${prevTick.momentum} -> ${currentTick.momentum}`);
}
```
**Severity**: Info / Warning.
**Purpose**: Notify observer of regime shifts or emergences.

## 2. System State Change (🟡 YELLOW)
**Trigger**: When `system_status.status` changes (e.g., `IDLE` -> `OBSERVING`).
**Logic**:
```javascript
if (currentStatus !== prevStatus) {
  alert(`System State Changed: ${prevStatus} -> ${currentStatus}`);
}
```
**Severity**: Info.

## 3. Data Staleness (🔴 RED)
**Trigger**: When `last_ev_tick` timestamp is older than `N` minutes (e.g. 15 mins for a 5-min cron).
**Logic**:
```javascript
const minutesSince = (now - lastTickTime) / 60000;
if (minutesSince > 15) {
  alert("Data Stale: Last tick was > 15 mins ago.");
}
```
**Severity**: Error.
**Action**: Investigation required (Manual).

## 4. Governance Violation (🔴 RED)
**Trigger**: When `governance_status` != `CLEAN`.
**Severity**: Critical.
**Action**: HALT (Passive).
