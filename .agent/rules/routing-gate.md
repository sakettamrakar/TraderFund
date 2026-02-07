---
trigger: always_on
---

rule_id: AG-GOV-ROUTING-001
description: Enforce governed execution path when governance_required=true
when:
  header.AG_ROUTING.governance_required: true
then:
  require:
    - GOVERNED_EXECUTION_ENVELOPE
else:
  allow: true
