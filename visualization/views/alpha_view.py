import streamlit as st
import pandas as pd
from pathlib import Path
from alpha_discovery.repository.parquet_repo import ParquetAlphaRepository

class AlphaExplorer:
    def __init__(self):
        self.repo = ParquetAlphaRepository(Path("data/alpha"))

    def render(self):
        st.header("🔬 Alpha Hypothesis Lab")
        
        alphas = self.repo.get_active_alphas()
        
        if not alphas:
            st.info("No alpha hypotheses discovered yet.")
            return

        st.metric("Total Hypotheses", len(alphas))
        
        for alpha in alphas:
            with st.container():
                st.subheader(f"{alpha.title}")
                st.caption(f"Pattern: {alpha.pattern_type.value} | State: {alpha.validation_state.value}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Confidence", f"{alpha.confidence_score:.1f}")
                    st.write(f"Source: {alpha.source_market.value} → Target: {alpha.target_market.value}")
                    
                with col2:
                    st.json(alpha.evidence_payload)
                
                st.markdown("---")
