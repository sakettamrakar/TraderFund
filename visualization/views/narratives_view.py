import streamlit as st
import pandas as pd
from pathlib import Path
from narratives.repository.parquet_repo import ParquetNarrativeRepository
from signals.core.enums import Market
from presentation.repository.parquet_repo import ParquetSummaryRepository

class NarrativeTimeline:
    def __init__(self):
        self.repo = ParquetNarrativeRepository(Path("data/narratives"))
        self.sum_repo = ParquetSummaryRepository(Path("data/presentation/summaries"))

    def render(self):
        st.header("📖 Market Narratives")
        
        market = st.selectbox("Market Context", [m.value for m in Market], key="nav_market")
        narratives = self.repo.get_active_narratives(Market(market))
        
        if not narratives:
            st.info("No active narratives found.")
            return
            
        st.write(f"Found {len(narratives)} ongoing stories.")
        
        for n in narratives:
            with st.expander(f"{n.title} (Conf: {n.confidence_score:.2f})"):
                # Try fetch summary
                summary = self.sum_repo.get_summary_by_narrative(n.narrative_id)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    if summary:
                        st.markdown(f"**{summary.headline}**")
                        st.write(summary.summary_text)
                    else:
                        st.caption("No AI summary generated yet.")
                        st.json(n.explainability_payload)
                        
                with col2:
                    st.metric("Events", len(n.supporting_events))
                    st.write(f"Assets: {', '.join(n.related_assets)}")
                    st.write(f"State: {n.lifecycle_state.value}")
