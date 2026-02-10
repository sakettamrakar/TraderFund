# Memory Quality Audit Report

**Generated**: 2026-02-10 21:47:51
**Script**: `scripts/memory_audit.py`
**Status**: READ-ONLY ANALYSIS — no files were modified

---

## Required Files

- ✅ **PASS**: `docs\memory\index.md` exists
- ✅ **PASS**: `docs\memory\QUALITY.md` exists
- ✅ **PASS**: `docs\memory\DECISION_PROTOCOL.md` exists
## Authority Invariant

- ✅ **PASS**: `vision` is defined in docs\memory\00_vision\vision.md
- ✅ **PASS**: `scope` is defined in docs\memory\01_scope\boundaries.md
- ✅ **PASS**: `decisions` is defined in docs\memory\decisions\README.md
## Explicit Non-Goals

- ✅ **PASS**: Explicit exclusion language found in boundaries.md
## Decision Traceability

- ✅ **PASS**: 16 ADR(s) found: ADR-0001.md, ADR-0002.md, ADR-0003.md, ADR-0004.md, ADR-0005.md, ADR-0006.md, ADR-0007.md, ADR-0008.md, ADR-0009.md, ADR-0010.md, ADR-0011.md, ADR-0012.md, ADR-0013.md, ADR-0014.md, ADR-0015.md, ADR-0016.md
## Intent vs Implementation

- ✅ **PASS**: No large code blocks found in memory files
## Update Locality

- ⚠️ **WARN**: Heading overlap between `docs\memory\00_vision\vision.md` and `docs\memory\03_domain\domain_model.md`: cognitive, hierarchy, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\00_vision\vision.md` and `docs\memory\04_architecture\macro.md`: cognitive, core, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\01_scope\boundaries.md` and `docs\memory\02_success\success_criteria.md`: criteria, exit, intelligence, mode, portfolio
- ⚠️ **WARN**: Heading overlap between `docs\memory\01_scope\boundaries.md` and `docs\memory\06_data\data_contracts.md`: portfolio, profile, three
- ⚠️ **WARN**: Heading overlap between `docs\memory\01_scope\boundaries.md` and `docs\memory\07_execution\runtime.md`: criteria, intelligence, mode, shadow
- ⚠️ **WARN**: Heading overlap between `docs\memory\01_scope\boundaries.md` and `docs\memory\08_reliability\failure_model.md`: mode, shadow, validation
- ⚠️ **WARN**: Heading overlap between `docs\memory\01_scope\boundaries.md` and `docs\memory\11_deployment\evolution.md`: criteria, exit, intelligence, research, three
- ⚠️ **WARN**: Heading overlap between `docs\memory\01_scope\boundaries.md` and `docs\memory\decisions\ADR-0004.md`: mode, shadow, validation
- ⚠️ **WARN**: Heading overlap between `docs\memory\02_success\success_criteria.md` and `docs\memory\03_domain\domain_model.md`: discovery, intelligence, opportunity, portfolio, regime
- ⚠️ **WARN**: Heading overlap between `docs\memory\02_success\success_criteria.md` and `docs\memory\04_architecture\macro.md`: dashboard, discovery, intelligence, layer, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\02_success\success_criteria.md` and `docs\memory\05_components\component_validation_report.md`: criteria, observability, success
- ⚠️ **WARN**: Heading overlap between `docs\memory\02_success\success_criteria.md` and `docs\memory\06_data\data_contracts.md`: dashboard, portfolio, regime
- ⚠️ **WARN**: Heading overlap between `docs\memory\02_success\success_criteria.md` and `docs\memory\07_execution\runtime.md`: criteria, dashboard, intelligence, mode, shadow
- ⚠️ **WARN**: Heading overlap between `docs\memory\02_success\success_criteria.md` and `docs\memory\08_reliability\failure_model.md`: dashboard, layer, mode, regime, shadow
- ⚠️ **WARN**: Heading overlap between `docs\memory\02_success\success_criteria.md` and `docs\memory\10_observability\metrics.md`: criteria, dashboard, observability, regime, signal
- ⚠️ **WARN**: Heading overlap between `docs\memory\02_success\success_criteria.md` and `docs\memory\11_deployment\evolution.md`: criteria, exit, intelligence, layer
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\04_architecture\macro.md`: cognitive, constraints, convergence, discovery, intelligence
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\constraint_engine.yaml`: constraints, execution, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\convergence_engine.yaml`: convergence, level, scoring
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\factor_engine.yaml`: analysis, factor, level, reward
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\factor_lens.yaml`: discovery, factor, level, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\fundamental_lens.yaml`: discovery, level, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\meta_engine.yaml`: analysis, filter, level, meta, trust
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\narrative_engine.yaml`: change, explanation, level, narrative
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\narrative_lens.yaml`: discovery, level, narrative, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\portfolio_intelligence.yaml`: intelligence, level, portfolio
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\regime_engine.yaml`: level, reality, regime
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\strategy_lens.yaml`: discovery, level, opportunity, parallel, strategy
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\strategy_selector.yaml`: level, playbook, selection, strategy
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\05_components\technical_lens.yaml`: discovery, level, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\06_data\data_contracts.md`: cognitive, factor, portfolio, regime, strategy
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\08_reliability\failure_model.md`: analysis, convergence, execution, factor, meta
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\09_security\trust.md`: execution, hierarchy, strategy, trust
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\10_observability\metrics.md`: constraints, execution, narrative, regime, strategy
- ⚠️ **WARN**: Heading overlap between `docs\memory\03_domain\domain_model.md` and `docs\memory\ledger.md`: constraints, hierarchy, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\data_flow.md` and `docs\memory\04_architecture\macro.md`: architecture, cognitive, conflicts, ingestion, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\data_flow.md` and `docs\memory\05_components\component_validation_report.md`: conflicts, questions, resolved
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\data_flow.md` and `docs\memory\06_data\data_contracts.md`: canonical, cognitive, daily, final, india
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\data_flow.md` and `docs\memory\07_execution\runtime.md`: canonical, india, ingestion, lifecycle, pipeline
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\data_flow.md` and `docs\memory\08_reliability\failure_model.md`: india, ingestion, state
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\data_flow.md` and `docs\memory\10_observability\metrics.md`: architecture, ingestion, pipeline, state
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\data_flow.md` and `docs\memory\11_deployment\evolution.md`: canonical, ingestion, process, research, state
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\component_validation_report.md`: component, conflicts, mapping, questions, resolved
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\constraint_engine.yaml`: component, constraints, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\convergence_engine.yaml`: component, convergence, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\dashboard.yaml`: component, dashboard, layer, level, observation
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\factor_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\factor_lens.yaml`: component, discovery, level, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\fundamental_lens.yaml`: component, discovery, level, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\governance.yaml`: component, governance, layer, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\ingestion_events.yaml`: component, foundation, ingestion, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\ingestion_india.yaml`: component, foundation, ingestion, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\ingestion_us.yaml`: component, foundation, ingestion, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\meta_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\momentum_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\narrative_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\narrative_lens.yaml`: component, discovery, level, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\portfolio_intelligence.yaml`: component, intelligence, level, portfolio
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\regime_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\strategy_lens.yaml`: component, discovery, level, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\05_components\technical_lens.yaml`: component, discovery, level, opportunity, parallel
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\06_data\data_contracts.md`: cognitive, dashboard, ingestion, legacy, macro
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\07_execution\runtime.md`: dashboard, global, ingestion, intelligence, legacy
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\08_reliability\failure_model.md`: component, convergence, dashboard, engine, governance
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\09_security\trust.md`: core, governance, layer, legacy, mapping
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\10_observability\metrics.md`: architecture, constraints, core, dashboard, definitions
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\11_deployment\evolution.md`: engine, foundation, global, governance, ingestion
- ⚠️ **WARN**: Heading overlap between `docs\memory\04_architecture\macro.md` and `docs\memory\governance.md`: constraints, core, governance
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\component_validation_report.md` and `docs\memory\08_reliability\failure_model.md`: component, mapping, summary, validation
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\component_validation_report.md` and `docs\memory\10_observability\metrics.md`: criteria, integrity, mapping, observability, success
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\component_validation_report.md` and `docs\memory\11_deployment\evolution.md`: criteria, mandatory, mapping, summary
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\constraint_engine.yaml` and `docs\memory\05_components\convergence_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\constraint_engine.yaml` and `docs\memory\05_components\factor_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\constraint_engine.yaml` and `docs\memory\05_components\meta_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\constraint_engine.yaml` and `docs\memory\05_components\momentum_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\constraint_engine.yaml` and `docs\memory\05_components\narrative_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\constraint_engine.yaml` and `docs\memory\05_components\regime_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\constraint_engine.yaml` and `docs\memory\08_reliability\failure_model.md`: component, engine, execution
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\convergence_engine.yaml` and `docs\memory\05_components\factor_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\convergence_engine.yaml` and `docs\memory\05_components\meta_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\convergence_engine.yaml` and `docs\memory\05_components\momentum_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\convergence_engine.yaml` and `docs\memory\05_components\narrative_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\convergence_engine.yaml` and `docs\memory\05_components\regime_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\convergence_engine.yaml` and `docs\memory\08_reliability\failure_model.md`: component, convergence, engine
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\dashboard.yaml` and `docs\memory\05_components\governance.yaml`: component, cross, cutting, layer, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\dashboard.yaml` and `docs\memory\08_reliability\failure_model.md`: component, dashboard, layer
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_engine.yaml` and `docs\memory\05_components\factor_lens.yaml`: component, factor, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_engine.yaml` and `docs\memory\05_components\meta_engine.yaml`: analysis, component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_engine.yaml` and `docs\memory\05_components\momentum_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_engine.yaml` and `docs\memory\05_components\narrative_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_engine.yaml` and `docs\memory\05_components\regime_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_engine.yaml` and `docs\memory\08_reliability\failure_model.md`: analysis, component, engine, factor
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_lens.yaml` and `docs\memory\05_components\fundamental_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_lens.yaml` and `docs\memory\05_components\narrative_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_lens.yaml` and `docs\memory\05_components\strategy_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_lens.yaml` and `docs\memory\05_components\technical_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\factor_lens.yaml` and `docs\memory\08_reliability\failure_model.md`: component, factor, lens
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\fundamental_lens.yaml` and `docs\memory\05_components\narrative_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\fundamental_lens.yaml` and `docs\memory\05_components\strategy_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\fundamental_lens.yaml` and `docs\memory\05_components\technical_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\fundamental_lens.yaml` and `docs\memory\08_reliability\failure_model.md`: component, fundamental, lens
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\governance.yaml` and `docs\memory\05_components\meta_engine.yaml`: component, level, meta
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\governance.yaml` and `docs\memory\08_reliability\failure_model.md`: component, governance, layer, meta
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\ingestion_events.yaml` and `docs\memory\05_components\ingestion_india.yaml`: component, foundation, ingestion, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\ingestion_events.yaml` and `docs\memory\05_components\ingestion_us.yaml`: component, foundation, ingestion, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\ingestion_events.yaml` and `docs\memory\06_data\data_contracts.md`: event, ingestion, pipeline
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\ingestion_india.yaml` and `docs\memory\05_components\ingestion_us.yaml`: component, foundation, ingestion, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\ingestion_india.yaml` and `docs\memory\08_reliability\failure_model.md`: component, india, ingestion
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\meta_engine.yaml` and `docs\memory\05_components\momentum_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\meta_engine.yaml` and `docs\memory\05_components\narrative_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\meta_engine.yaml` and `docs\memory\05_components\regime_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\meta_engine.yaml` and `docs\memory\08_reliability\failure_model.md`: analysis, component, engine, meta
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\momentum_engine.yaml` and `docs\memory\05_components\narrative_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\momentum_engine.yaml` and `docs\memory\05_components\regime_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\narrative_engine.yaml` and `docs\memory\05_components\narrative_lens.yaml`: component, level, narrative
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\narrative_engine.yaml` and `docs\memory\05_components\regime_engine.yaml`: component, engine, level
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\narrative_engine.yaml` and `docs\memory\08_reliability\failure_model.md`: component, engine, narrative
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\narrative_lens.yaml` and `docs\memory\05_components\strategy_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\narrative_lens.yaml` and `docs\memory\05_components\technical_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\narrative_lens.yaml` and `docs\memory\08_reliability\failure_model.md`: component, lens, narrative
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\regime_engine.yaml` and `docs\memory\08_reliability\failure_model.md`: component, engine, regime
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\strategy_lens.yaml` and `docs\memory\05_components\strategy_selector.yaml`: component, level, strategy
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\strategy_lens.yaml` and `docs\memory\05_components\technical_lens.yaml`: component, discovery, lens, level, opportunity
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\strategy_lens.yaml` and `docs\memory\08_reliability\failure_model.md`: component, lens, strategy
- ⚠️ **WARN**: Heading overlap between `docs\memory\05_components\strategy_selector.yaml` and `docs\memory\08_reliability\failure_model.md`: component, selector, strategy
- ⚠️ **WARN**: Heading overlap between `docs\memory\06_data\data_contracts.md` and `docs\memory\07_execution\runtime.md`: canonical, contract, cross, dashboard, evaluation
- ⚠️ **WARN**: Heading overlap between `docs\memory\06_data\data_contracts.md` and `docs\memory\08_reliability\failure_model.md`: alpha, dashboard, factor, india, ingestion
- ⚠️ **WARN**: Heading overlap between `docs\memory\06_data\data_contracts.md` and `docs\memory\09_security\trust.md`: contract, isolation, legacy, mapping, retention
- ⚠️ **WARN**: Heading overlap between `docs\memory\06_data\data_contracts.md` and `docs\memory\10_observability\metrics.md`: binding, dashboard, ingestion, legacy, mapping
- ⚠️ **WARN**: Heading overlap between `docs\memory\06_data\data_contracts.md` and `docs\memory\11_deployment\evolution.md`: canonical, contracts, evaluation, ingestion, layers
- ⚠️ **WARN**: Heading overlap between `docs\memory\06_data\data_contracts.md` and `docs\memory\governance.md`: contract, policy, truth
- ⚠️ **WARN**: Heading overlap between `docs\memory\06_data\data_contracts.md` and `docs\memory\ledger.md`: immutability, only, policy, registry, retention
- ⚠️ **WARN**: Heading overlap between `docs\memory\07_execution\runtime.md` and `docs\memory\08_reliability\failure_model.md`: active, batch, dashboard, execution, gate
- ⚠️ **WARN**: Heading overlap between `docs\memory\07_execution\runtime.md` and `docs\memory\09_security\trust.md`: contract, execution, handling, legacy, mapping
- ⚠️ **WARN**: Heading overlap between `docs\memory\07_execution\runtime.md` and `docs\memory\10_observability\metrics.md`: criteria, dashboard, execution, harness, ingestion
- ⚠️ **WARN**: Heading overlap between `docs\memory\07_execution\runtime.md` and `docs\memory\11_deployment\evolution.md`: advancement, canonical, criteria, emergency, evaluation
- ⚠️ **WARN**: Heading overlap between `docs\memory\07_execution\runtime.md` and `docs\memory\DECISION_PROTOCOL.md`: escalation, override, protocol
- ⚠️ **WARN**: Heading overlap between `docs\memory\07_execution\runtime.md` and `docs\memory\governance.md`: advancement, automation, contract, escalation, principles
- ⚠️ **WARN**: Heading overlap between `docs\memory\07_execution\runtime.md` and `docs\memory\ledger.md`: automation, limits, only, truth
- ⚠️ **WARN**: Heading overlap between `docs\memory\08_reliability\failure_model.md` and `docs\memory\09_security\trust.md`: execution, governance, handling, layer, legacy
- ⚠️ **WARN**: Heading overlap between `docs\memory\08_reliability\failure_model.md` and `docs\memory\10_observability\metrics.md`: dashboard, execution, governance, harness, ingestion
- ⚠️ **WARN**: Heading overlap between `docs\memory\08_reliability\failure_model.md` and `docs\memory\11_deployment\evolution.md`: drift, engine, epistemic, gate, governance
- ⚠️ **WARN**: Heading overlap between `docs\memory\08_reliability\failure_model.md` and `docs\memory\decisions\ADR-0004.md`: decision, mode, shadow, validation
- ⚠️ **WARN**: Heading overlap between `docs\memory\08_reliability\failure_model.md` and `docs\memory\ledger.md`: epistemic, policy, registry, temporal
- ⚠️ **WARN**: Heading overlap between `docs\memory\08_reliability\failure_model.md` and `docs\memory\QUALITY.md`: decision, detection, drift
- ⚠️ **WARN**: Heading overlap between `docs\memory\09_security\trust.md` and `docs\memory\10_observability\metrics.md`: core, execution, forbidden, governance, legacy
- ⚠️ **WARN**: Heading overlap between `docs\memory\09_security\trust.md` and `docs\memory\11_deployment\evolution.md`: authority, forbidden, governance, layer, legacy
- ⚠️ **WARN**: Heading overlap between `docs\memory\09_security\trust.md` and `docs\memory\decisions\ADR-0011.md`: governance, human, multi
- ⚠️ **WARN**: Heading overlap between `docs\memory\09_security\trust.md` and `docs\memory\governance.md`: chat, contract, core, credential, forbidden
- ⚠️ **WARN**: Heading overlap between `docs\memory\09_security\trust.md` and `docs\memory\ledger.md`: authority, hierarchy, retention
- ⚠️ **WARN**: Heading overlap between `docs\memory\09_security\trust.md` and `docs\memory\QUALITY.md`: authority, contract, safety, separation
- ⚠️ **WARN**: Heading overlap between `docs\memory\10_observability\metrics.md` and `docs\memory\11_deployment\evolution.md`: criteria, forbidden, governance, ingestion, legacy
- ⚠️ **WARN**: Heading overlap between `docs\memory\10_observability\metrics.md` and `docs\memory\governance.md`: constraints, core, forbidden, governance
- ⚠️ **WARN**: Heading overlap between `docs\memory\11_deployment\evolution.md` and `docs\memory\DECISION_PROTOCOL.md`: override, protocol, structural
- ⚠️ **WARN**: Heading overlap between `docs\memory\11_deployment\evolution.md` and `docs\memory\decisions\ADR-0005.md`: epistemic, freeze, protocol
- ⚠️ **WARN**: Heading overlap between `docs\memory\11_deployment\evolution.md` and `docs\memory\governance.md`: actions, advancement, forbidden, governance, module
- ⚠️ **WARN**: Heading overlap between `docs\memory\11_deployment\evolution.md` and `docs\memory\ledger.md`: authority, epistemic, truth
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0002.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0003.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0004.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0005.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0006.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0007.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0008.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0009.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0010.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0011.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0012.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0013.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0014.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0015.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0001.md` and `docs\memory\decisions\ADR-0016.md`: consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0003.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0004.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0005.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0006.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0007.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0008.md`: alternatives, consequences, decision, evidence, execution
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0009.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0010.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0002.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0004.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0005.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0006.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0007.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0008.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0009.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0010.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, first
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0003.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0005.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0006.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0007.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0008.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0009.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0010.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0004.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0006.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0007.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0008.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0009.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0010.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0005.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0007.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0008.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0009.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0010.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0006.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0008.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0009.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0010.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0007.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0008.md` and `docs\memory\decisions\ADR-0009.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0008.md` and `docs\memory\decisions\ADR-0010.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0008.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0008.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0008.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0008.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0008.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0008.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0009.md` and `docs\memory\decisions\ADR-0010.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0009.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0009.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0009.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0009.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0009.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0009.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0010.md` and `docs\memory\decisions\ADR-0011.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0010.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0010.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0010.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0010.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0010.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0011.md` and `docs\memory\decisions\ADR-0012.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0011.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0011.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0011.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0011.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0012.md` and `docs\memory\decisions\ADR-0013.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0012.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0012.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0012.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0013.md` and `docs\memory\decisions\ADR-0014.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0013.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0013.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0014.md` and `docs\memory\decisions\ADR-0015.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0014.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\decisions\ADR-0015.md` and `docs\memory\decisions\ADR-0016.md`: alternatives, consequences, decision, evidence, rationale
- ⚠️ **WARN**: Heading overlap between `docs\memory\governance.md` and `docs\memory\ledger.md`: automation, conflict, constraints, policy, resolution
## Machine Parsability

- ✅ **PASS**: All markdown memory files contain structured headings
## Drift Detection

- ✅ **PASS**: No [TBD] markers found — all sections appear populated
## Regeneration Safety

- ⚠️ **WARN**: Directory `_appendix/` exists but is not referenced in index.md

---

## Summary

| Status | Count |
| :--- | :--- |
| ✅ PASS | 11 |
| ⚠️ WARN | 279 |
| ❌ FAIL | 0 |
