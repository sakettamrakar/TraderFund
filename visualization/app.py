import streamlit as st
from visualization.configs.styles import VisualStyles
from visualization.views.signals_view import SignalExplorer
from visualization.views.narratives_view import NarrativeTimeline
from visualization.views.alpha_view import AlphaExplorer

def main():
    st.set_page_config(
        page_title=VisualStyles.APP_TITLE,
        page_icon=VisualStyles.APP_ICON,
        layout="wide"
    )
    
    st.title(f"{VisualStyles.APP_ICON} {VisualStyles.APP_TITLE}")
    st.info(VisualStyles.WARNING_BANNER)
    
    # Navigation
    tab1, tab2, tab3 = st.tabs(["Signals 📡", "Narratives 📖", "Alpha Research 🔬"])
    
    with tab1:
        SignalExplorer().render()
        
    with tab2:
        NarrativeTimeline().render()
        
    with tab3:
        AlphaExplorer().render()
        
    # Sidebar Metadata
    st.sidebar.markdown("### System Status")
    st.sidebar.success("Core Engine: ONLINE")
    st.sidebar.success("Intelligence: ONLINE")
    st.sidebar.info("Mode: READ-ONLY (Research)")

if __name__ == "__main__":
    main()
