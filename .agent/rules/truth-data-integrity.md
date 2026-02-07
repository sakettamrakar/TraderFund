---
trigger: always_on
---

rule_id: AG-GOV-TRUTH-003
when:
  header.AG_ROUTING.governance_required: true
then:
  assert_all:
    - GOVERNED_EXECUTION_ENVELOPE.truth.frozen == true
    - GOVERNED_EXECUTION_ENVELOPE.truth.data_mode == "REAL_ONLY"
    - GOVERNED_EXECUTION_ENVELOPE.truth.mock_data_present == false
