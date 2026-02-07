# Integration Reality Run — Failure Log

## 1. Purpose
This log captures all failures, errors, and exceptional conditions encountered during the IRR.
Failures are opportunities to strengthen the system.

---

## 2. Failure Classification

| Severity | Description |
| :--- | :--- |
| **CRITICAL** | Blocks execution, data integrity at risk |
| **ERROR** | Computation failed, fallback engaged |
| **WARNING** | Edge case detected, degraded output |
| **INFO** | Expected limitation, documented |

---

## 3. Failure Log

### 3.1. US Market Failures

| ID | Severity | Layer | Description | Resolution |
| :--- | :--- | :--- | :--- | :--- |
| `F-US-001` | WARNING | FRAGILITY | VIX level (101.58) exceeds normal range | Likely stale data; verify data freshness |
| `F-US-002` | INFO | DECISION | Regime BEARISH forced entry blocks | Expected behavior under bearish conditions |
| `F-US-003` | WARNING | FACTOR | Factor context age > 6 hours | Recalculation recommended |

### 3.2. India Market Failures

| ID | Severity | Layer | Description | Resolution |
| :--- | :--- | :--- | :--- | :--- |
| `F-IND-001` | INFO | DATA | IN10Y is monthly (72 obs), not daily | Documented limitation; frequency mismatch acceptable |
| `F-IND-002` | INFO | REGIME | Regime NEUTRAL limits entry permissions | Expected behavior |

### 3.3. Cross-Market Failures

| ID | Severity | Layer | Description | Resolution |
| :--- | :--- | :--- | :--- | :--- |
| `F-CROSS-001` | INFO | DASHBOARD | Market selector requires backend restart for new data | Document in operational procedures |

---

## 4. Unresolved Failures

| ID | Severity | Description | Owner | Due |
| :--- | :--- | :--- | :--- | :--- |
| `F-US-001` | WARNING | VIX data appears stale or anomalous | Data Ops | 2026-01-31 |

---

## 5. Failure Trends

| Pattern | Count | Mitigation |
| :--- | :--- | :--- |
| Stale data warnings | 2 | Implement automated freshness checks |
| Regime edge cases | 1 | Add TRANSITION handling |
| Frequency mismatch | 1 | Document in data contract |

---

## 6. Conclusion
No CRITICAL failures detected.
2 WARNING level issues require attention.
System is operationally sound with documented limitations.
