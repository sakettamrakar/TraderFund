from __future__ import annotations

from typing import Any, Dict, List


class PortfolioNarrativeSynthesizer:
    """Optional synthesis layer for human-readable portfolio research narratives."""

    def synthesize(
        self,
        *,
        suggestions: List[Dict[str, Any]],
        research_profiles: List[Dict[str, Any]],
        portfolio_event_alerts: List[Dict[str, Any]] | None = None,
        enable_llm: bool = False,
    ) -> Dict[str, Any]:
        portfolio_event_alerts = portfolio_event_alerts or []
        if enable_llm:
            mode = "LLM_OPTIONAL_DISABLED_IN_RUNTIME"
        else:
            mode = "DETERMINISTIC_TEMPLATE"

        lead = suggestions[0]["detail"] if suggestions else "Portfolio research is balanced with no dominant advisory signal."
        highlighted = ", ".join(profile["ticker"] for profile in research_profiles[:3])
        event_summary = None
        if portfolio_event_alerts:
            first_event = portfolio_event_alerts[0]
            event_summary = f"Material event watch: {first_event.get('ticker')} — {first_event.get('event_summary')}"
        return {
            "mode": mode,
            "portfolio_narrative": f"Portfolio research indicates: {lead}" + (f" {event_summary}" if event_summary else ""),
            "research_style_summary": f"Primary holdings under review include {highlighted}. Output is advisory only and does not authorize trading.",
            "event_narrative": event_summary,
            "advisory_only": True,
        }