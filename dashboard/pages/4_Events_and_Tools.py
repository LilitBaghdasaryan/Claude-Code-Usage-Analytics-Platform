import streamlit as st
from database import run_query
import queries as q
from utils import plot_bar, plot_pie, plot_stacked_bar

st.set_page_config(page_title="Events and Tools")

# Event Type Distribution
st.header("Most Common Event Types")
df_events = run_query(q.COMMON_EVENTS)
if df_events.empty:
    st.warning("No data available.")
else:
    df_events["event_type"] = df_events["event_type"].fillna("Unknown")
    plot_bar(df_events, "event_type", "frequency", "Event Type Distribution", xlabel="Event Type", ylabel="Frequency")
    plot_pie(df_events, "frequency", "event_type", "Event Type Share")

# Tool Decisions
st.header("Tool Acceptance vs Rejection")
df_tool = run_query(q.TOOL_DECISIONS)
if df_tool.empty:
    st.warning("No data available.")
else:
    df_tool_pivot = df_tool.pivot(index='tool_name', columns='decision', values='count').fillna(0)
    plot_stacked_bar(df_tool_pivot, "Tool name", None, "Tool Decisions")