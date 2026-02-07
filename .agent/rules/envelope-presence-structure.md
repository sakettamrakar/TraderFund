---
trigger: always_on
---

rule_id: AG-GOV-STRUCTURE-002
when:
  header.AG_ROUTING.governance_required: true
then:
  require_fields:
    - GOVERNED_EXECUTION_ENVELOPE.meta
    - GOVERNED_EXECUTION_ENVELOPE.truth
    - GOVERNED_EXECUTION_ENVELOPE.scope
    - GOVERNED_EXECUTION_ENVELOPE.invariants
    - GOVERNED_EXECUTION_ENVELOPE.obligations
    - GOVERNED_EXECUTION_ENVELOPE.task
