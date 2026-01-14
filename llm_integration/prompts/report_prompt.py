"""
Report Explanation Prompt Template.
Converts structured Report JSON into human-readable summary.
"""

SYSTEM_PROMPT = """You are a neutral market research analyst summarizing institutional reports.

STRICT RULES:
1. Summarize WHAT changed since the last report.
2. Explain WHY it changed using provided evidence.
3. Acknowledge WHAT remains unclear.
4. Maintain neutral, institutional tone throughout.
5. Do NOT speculate beyond provided data.

FORBIDDEN:
- Future predictions
- Trading recommendations
- Emotional language
- New facts not in input
"""

REPORT_PROMPT_TEMPLATE = """
Summarize the following market intelligence report. Use ONLY the provided information.

INPUT DATA:
```json
{{
  "report_id": "{report_id}",
  "report_type": "{report_type}",
  "market_scope": "{market_scope}",
  "period_start": "{period_start}",
  "period_end": "{period_end}",
  "included_narratives": {included_narratives},
  "confidence_overview": "{confidence_overview}",
  "change_summary": {change_summary}
}}
```

Provide a summary covering:
1. Key themes in this report
2. What changed vs prior period
3. What remains uncertain
4. Overall confidence interpretation

Remember: NO predictions, NO advice.
"""

def build_report_prompt(report_dict: dict) -> str:
    return REPORT_PROMPT_TEMPLATE.format(
        report_id=report_dict.get('report_id', 'UNKNOWN'),
        report_type=report_dict.get('report_type', 'UNKNOWN'),
        market_scope=report_dict.get('market_scope', 'UNKNOWN'),
        period_start=report_dict.get('period_start', ''),
        period_end=report_dict.get('period_end', ''),
        included_narratives=report_dict.get('included_narratives', []),
        confidence_overview=report_dict.get('confidence_overview', ''),
        change_summary=report_dict.get('change_summary', {})
    )
