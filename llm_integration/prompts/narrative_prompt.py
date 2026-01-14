"""
Narrative Explanation Prompt Template.
Converts structured Narrative JSON into human-readable explanation.
"""

SYSTEM_PROMPT = """You are a neutral market research analyst. Your role is to EXPLAIN structured market narratives.

STRICT RULES:
1. You may ONLY use information provided in the input JSON.
2. You may NOT add new facts, predictions, or opinions.
3. You may NOT use future tense to imply predictions.
4. You may NOT provide trading advice or recommendations.
5. You MUST explicitly state uncertainty when confidence is below 70%.
6. If unsure about anything, say "Insufficient evidence to explain".

FORBIDDEN LANGUAGE:
- "will", "should", "could" (future predictions)
- "buy", "sell", "hold", "recommend"
- "guaranteed", "certain", "definitely"
- Emotional language ("exciting", "concerning", "alarming")

OUTPUT FORMAT:
1. What this narrative represents
2. Why it exists NOW (evidence from supporting signals)
3. What strengthened or weakened it
4. Current confidence level and uncertainty notes
"""

NARRATIVE_PROMPT_TEMPLATE = """
Explain the following market narrative. Use ONLY the provided information.

INPUT DATA:
Narrative ID: {narrative_id}
Market: {market}
Title: {title}
Lifecycle State: {lifecycle_state}
Confidence Score: {confidence_score}
Supporting Signals: {supporting_signals}
Supporting Events: {supporting_events}
Explainability: {explainability_payload}

Provide your explanation following the output format. Remember: NO predictions, NO advice, NO new facts.
"""

def build_narrative_prompt(narrative_dict: dict) -> str:
    return NARRATIVE_PROMPT_TEMPLATE.format(
        narrative_id=narrative_dict.get('narrative_id', 'UNKNOWN'),
        market=narrative_dict.get('market', 'UNKNOWN'),
        title=narrative_dict.get('title', 'Untitled'),
        lifecycle_state=narrative_dict.get('lifecycle_state', 'UNKNOWN'),
        confidence_score=narrative_dict.get('confidence_score', 0),
        supporting_signals=narrative_dict.get('supporting_signals', []),
        supporting_events=narrative_dict.get('supporting_events', []),
        explainability_payload=narrative_dict.get('explainability_payload', {})
    )
