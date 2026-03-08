"""Scheduler - Workflows Definitions"""
from typing import List
from .models import Task

def get_daily_workflow(include_validation_review: bool = False) -> List[Task]:
    """Define the Daily Post-Market Flow."""
    tasks = []
    
    # 0. Core Proxy & Evolution Refresh
    tasks.append(Task(
        name="core_proxy_refresh",
        module_path="scripts.scheduled_evolution_refresh",
        function_name="main",
        kwargs={},
        description="Daily incremental refresh of core market proxies, parity, and ev_tick"
    ))

    # 1. Historical Backfill (Expansion)
    tasks.append(Task(
        name="historical_backfill",
        module_path="ingestion.historical_backfill.runner",
        function_name="run_backfill",
        kwargs={"budget": 50}, # Shares global budget of 50
        dependencies=["core_proxy_refresh"],
        description="Daily incremental universe expansion"
    ))

    # 2. Incremental Update
    tasks.append(Task(
        name="incremental_update",
        module_path="ingestion.incremental_update.runner",
        function_name="run_incremental_update",
        kwargs={"budget": 50},
        dependencies=["historical_backfill"],
        description="Fetch latest daily data"
    ))
    
    # 2. Pipeline Controller
    tasks.append(Task(
        name="pipeline_controller",
        module_path="research_modules.pipeline_controller.runner",
        function_name="run_pipeline_orchestration",
        dependencies=["incremental_update"],
        description="Decide and run analysis stages"
    ))
    
    # 3. Narrative Evolution (Runs after analysis)
    tasks.append(Task(
        name="narrative_evolution",
        module_path="research_modules.narrative_evolution.runner",
        function_name="run_narrative_generation",
        dependencies=["pipeline_controller"],
        description="Update narrative states"
    ))
    
    # 4. Narrative Diff
    tasks.append(Task(
        name="narrative_diff",
        module_path="research_modules.narrative_diff.runner",
        function_name="run_diff_detection",
        dependencies=["narrative_evolution"],
        description="Detect changes"
    ))
    
    # 5. Research Output
    tasks.append(Task(
        name="research_output",
        module_path="research_modules.research_output.runner",
        function_name="run_research_output",
        kwargs={"report_type": "daily"},
        dependencies=["narrative_diff"],
        description="Generate Daily Brief"
    ))
    
    # 6. Validation Log (Research only)
    tasks.append(Task(
        name="validation_log",
        module_path="research_modules.validation.logger",
        function_name="log_validation_snapshot",
        dependencies=["research_output"],
        description="Log snapshot for research validation"
    ))

    if include_validation_review:
        tasks.append(Task(
            name="daily_validation_review",
            module_path="traderfund.validation.daily_review",
            function_name="run_daily_validation_review",
            kwargs={"market": "US"},
            dependencies=["validation_log"],
            description="Aggregate latest self-healing validation summaries into a daily review"
        ))
    
    return tasks

def get_weekly_workflow() -> List[Task]:
    """Define Weekly Maintenance Flow."""
    tasks = []
    
    # 0. Anchor Data Refresh
    tasks.append(Task(
        name="anchor_data_refresh",
        module_path="scripts.scheduled_anchor_refresh",
        function_name="main",
        kwargs={},
        description="Weekly refresh of long-term structural datasets"
    ))

    # 1. Hygiene
    tasks.append(Task(
        name="universe_hygiene",
        module_path="research_modules.universe_hygiene.eligibility_runner",
        function_name="run_eligibility_evaluation",
        dependencies=["anchor_data_refresh"],
        description="Update universe eligibility"
    ))
    
    # 2. Backfill (Budgeted)
    tasks.append(Task(
        name="historical_backfill",
        module_path="ingestion.historical_backfill.runner",
        function_name="run_backfill",
        kwargs={"budget": 50},
        description="Backfill missing history"
    ))
    
    return tasks
