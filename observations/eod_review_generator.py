"""End-of-Day Review Generator.

Summarizes signal performance for the day and generates a report template
for final review.
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

def generate_eod_summary():
    date_str = datetime.now().strftime("%Y-%m-%d")
    review_file = Path(f"observations/signal_reviews/signals_for_review_{date_str}.csv")
    
    if not review_file.exists():
        print(f"No signals found for {date_str}.")
        return

    df = pd.read_csv(review_file)
    if df.empty:
        print("No signals to summarize.")
        return

    total_signals = len(df)
    
    # Map outcomes to quality buckets
    # A: Clean with high volume
    # B: Clean or Choppy with steady volume
    # C: Choppy/False but stuck at entry
    # D: False / Stopped out
    
    def classify_bucket(row):
        outcome = str(row.get('outcome', ''))
        vol = str(row.get('volume_continuation', ''))
        
        if outcome == "Clean" and vol == "Surge":
            return "A"
        elif outcome == "Clean":
            return "B"
        elif outcome == "Choppy":
            return "C"
        else:
            return "D"

    df['quality_bucket'] = df.apply(classify_bucket, axis=1)
    buckets = df['quality_bucket'].value_counts().to_dict()
    
    # Identify failure patterns
    false_signals = df[df['outcome'] == "False"]
    symbol_failures = false_signals['symbol'].value_counts().head(3).to_dict()

    # Calculate performance insights
    avg_conf_success = df[df['outcome'] == "Clean"]['confidence'].mean()
    avg_conf_failure = df[df['outcome'] == "False"]['confidence'].mean()

    avg_conf_success_str = f"{avg_conf_success:.2f}" if pd.notna(avg_conf_success) else "N/A"
    avg_conf_failure_str = f"{avg_conf_failure:.2f}" if pd.notna(avg_conf_failure) else "N/A"

    summary_content = f"""# End-of-Day Signal Review: {date_str}

## Summary Metrics
- **Total Signals Generated**: {total_signals}
- **Quality Distribution**:
  - Bucket A (High Quality): {buckets.get('A', 0)}
  - Bucket B (Moderate Quality): {buckets.get('B', 0)}
  - Bucket C (Choppy/No Follow-through): {buckets.get('C', 0)}
  - Bucket D (Failure/False Signal): {buckets.get('D', 0)}

## Performance Insights
- **Top Failing Symbols**: {", ".join([f"{k} ({v})" for k, v in symbol_failures.items()]) if symbol_failures else "None"}
- **Avg Confidence of Successes**: {avg_conf_success_str}
- **Avg Confidence of Failures**: {avg_conf_failure_str}

## Concrete Learnings (Manual Entry)
1. [Learning 1: Describe price action pattern observed]
2. [Learning 2: Note any volume divergence]
3. [Learning 3: Comment on overall market trend impact]

## Rules & Guardrails Check
- [ ] No mid-day logic tweaks? (Yes/No)
- [ ] No indicators added mid-observation? (Yes/No)
- [ ] Focus maintained on learning over P&L? (Yes/No)
"""

    report_path = Path(f"observations/signal_reviews/eod_report_{date_str}.md")
    with open(report_path, "w") as f:
        f.write(summary_content)
    
    print(f"Summary report generated: {report_path}")

if __name__ == "__main__":
    generate_eod_summary()
