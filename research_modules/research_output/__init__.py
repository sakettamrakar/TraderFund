"""Research Output Layer - Produces neutral, traceable research summaries"""
from .models import ResearchReport
from .generator import ReportGenerator
from .runner import run_research_output

__all__ = ["ResearchReport", "ReportGenerator", "run_research_output"]
