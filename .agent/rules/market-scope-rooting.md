---
trigger: always_on
---

rule_id: AG-GOV-SCOPE-004
when:
  header.AG_ROUTING.governance_required: true
then:
  assert_all:
    - GOVERNED_EXECUTION_ENVELOPE.scope.root_selector == "market"
    - GOVERNED_EXECUTION_ENVELOPE.scope.markets contains_any ["US", "INDIA"]
