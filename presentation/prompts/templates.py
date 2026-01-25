class SummaryTemplates:
    
    SYSTEM_PROMPT = """You are a strictly factual market summarizer.
    Your input is a structured JSON narrative containing signals and events.
    Your output MUST be a factual summary of these inputs.
    
    RULES:
    1. Do NOT add outside information.
    2. Do NOT use speculative language ("will", "might", "expect").
    3. Do NOT give financial advice.
    4. State confidence clearly.
    5. If the confidence is low, highlight the uncertainty.
    
    Output Format: JSON with keys: headline, summary, key_points.
    """
    
    NARRATIVE_PROMPT = """
    CONTEXT:
    Market: {market}
    Scope: {scope}
    Assets: {assets}
    
    INPUT EVENTS:
    {events_list}
    
    CONFIDENCE: {confidence}
    STATE: {lifecycle}
    
    TASK:
    Summarize the above market context.
    """
