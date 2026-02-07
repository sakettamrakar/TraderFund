---
trigger: always_on
---

rule_id: AG-GOV-INVARIANTS-005
when:
  header.AG_ROUTING.governance_required: true
then:
  assert_contains_all:
    - GOVERNED_EXECUTION_ENVELOPE.invariants:
        - INV-NO-EXECUTION
        - INV-NO-CAPITAL
        - INV-NO-SELF-ACTIVATION
        - INV-PROXY-CANONICAL
