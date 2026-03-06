import streamlit as st

st.set_page_config(page_title="Claude Analytics", layout="wide")

st.title("Claude Telemetry Dashboard")

st.markdown("""
Welcome to the analytics dashboard.

Use the sidebar to navigate between sections:
- Token Usage
- Cost Analysis
- User Analysis
- Events and Tools
- Anomaly Detection        
""")