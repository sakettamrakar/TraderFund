import logging
import json
from datetime import datetime
from typing import Dict
from narratives.core.models import Narrative
from presentation.core.models import NarrativeSummary
from presentation.prompts.templates import SummaryTemplates
from presentation.repository.base import SummaryRepository
from llm_integration.client import get_llm_client

logger = logging.getLogger("Summarizer")

class NarrativeSummarizer:
    def __init__(self, repo: SummaryRepository, llm_client=None):
        self.repo = repo
        self.llm = llm_client or get_llm_client()

    def _generate_mock_output(self, narrative: Narrative) -> Dict[str, str]:
        """Fallback mock generator if real LLM is unavailable."""
        return {
            "headline": f"Summary: {narrative.title}",
            "summary_text": f"Deterministic summary for {narrative.narrative_id}. LLM was unavailable.",
            "key_points": "- Point 1: Data analyzed\n- Point 2: Pattern identified"
        }

    def generate_summary(self, narrative: Narrative) -> NarrativeSummary:
        # 1. Prepare Prompt
        assets_str = ", ".join(narrative.related_assets)
        events_str = "\n".join(narrative.supporting_events) # Just IDs for now
        
        prompt = SummaryTemplates.NARRATIVE_PROMPT.format(
            market=narrative.market.value,
            scope=narrative.scope.value,
            assets=assets_str,
            events_list=events_str,
            confidence=narrative.confidence_score,
            lifecycle=narrative.lifecycle_state.value
        )
        
        # 2. Generate
        if self.llm is None:
            output = self._generate_mock_output(narrative)
            model_name = "MockLLM"
        else:
            # Use real LLM
            system_p = SummaryTemplates.SYSTEM_PROMPT
            raw_output = self.llm.generate(system_p, prompt)
            model_name = "LocalLLM"
            
            try:
                # Expecting JSON from LLM
                data = json.loads(raw_output)
                output = {
                    "headline": data.get("headline", narrative.title),
                    "summary_text": data.get("summary", "No summary provided."),
                    "key_points": data.get("key_points", "- No points provided.")
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON: {e}. Raw: {raw_output[:100]}...")
                # Fallback to a structured version of the raw output
                output = self._generate_mock_output(narrative)
                output['summary_text'] = raw_output

        # 3. Create Summary Object
        summary = NarrativeSummary.create(
            narrative_id=narrative.narrative_id,
            headline=output['headline'],
            text=output['summary_text'],
            points=output['key_points'],
            confidence=narrative.confidence_score, # Inherit for now
            metadata={"model": model_name, "prompt_len": len(prompt)}
        )
        
        # 4. Save
        self.repo.save_summary(summary)
        logger.info(f"Generated {model_name} Summary for {narrative.narrative_id}")
        return summary
