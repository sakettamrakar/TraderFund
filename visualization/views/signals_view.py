import streamlit as st
import pandas as pd
from pathlib import Path
from signals.repository.parquet_repo import ParquetSignalRepository
from signals.core.enums import Market
from visualization.configs.styles import VisualStyles

class SignalExplorer:
    def __init__(self):
        self.repo = ParquetSignalRepository(Path("data/signals"))

    def render(self):
        st.header("📡 Active Market Signals")
        
        market = st.selectbox("Select Market", [m.value for m in Market])
        
        # Load Signals
        signals = self.repo.get_active_signals(Market(market))
        
        if not signals:
            st.info("No active signals found for this market.")
            return

        # Convert to DataFrame for display
        data = []
        for s in signals:
            data.append({
                "Asset": s.asset_id,
                "Category": s.signal_category.value,
                "Direction": s.direction.value,
                "Strength": s.raw_strength,
                "Confidence": s.confidence_score if s.confidence_score else 0.0,
                "Horizon": s.expected_horizon,
                "ID": s.signal_id
            })
            
        df = pd.DataFrame(data)
        
        # Visual Filters
        min_conf = st.slider("Min Confidence", 0, 100, 50)
        filtered = df[df['Confidence'] >= min_conf]
        
        st.dataframe(
            filtered.style.applymap(
                lambda x: f"color: {VisualStyles.get_color_for_direction(x)}",
                subset=['Direction']
            )
        )
        
        # Details Drilldown
        st.subheader("Signal Details")
        selected_id = st.selectbox("Select Signal ID", filtered['ID'].unique())
        
        if selected_id:
            sig_obj = next(s for s in signals if s.signal_id == selected_id)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Confidence", f"{sig_obj.confidence_score:.1f}")
                st.json(sig_obj.explainability_payload)
            with col2:
                st.write(f"**Version**: {sig_obj.version}")
                st.write(f"**State**: {sig_obj.lifecycle_state.value}")
