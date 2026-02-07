---
trigger: always_on
---

rule_id: AG-GOV-ARTIFACTS-007
when:
  header.AG_ROUTING.governance_required: true
then:
  require_non_empty:
    - GOVERNED_EXECUTION_ENVELOPE.task.artifacts_expected
