import streamlit as st
import pandas as pd
from database import run_query
import queries as q
from utils import plot_bar, plot_line, plot_pie

st.set_page_config(page_title="Token Usage")

# Token Consumption by Role
st.header("Token Consumption by Role")
df_tokens = run_query(q.TOKEN_BY_ROLE)
if df_tokens.empty:
    st.warning("No data available.")
else:
    df_tokens["practice"] = df_tokens["practice"].fillna("Unknown")
    df_tokens["total_tokens"] = pd.to_numeric(df_tokens["total_tokens"], errors="coerce").fillna(0)
    plot_bar(df_tokens, "practice", "total_tokens", "Total Token Usage by Role", xlabel="Role", ylabel="Total Tokens")
    plot_pie(df_tokens, "total_tokens", "practice", "Token Usage Share by Role")

# Peak Usage
st.header("Peak Usage Times")
df_hour = run_query(q.USAGE_HOURS)
if df_hour.empty:
    st.warning("No data available.")
else:
    plot_line(df_hour, "hour", "total_events", "Usage by Hour", xlabel="Hour of Day", ylabel="Number of Events", rotate=False)

# Token Usage Over Time
st.header("Token Usage Over Time")
agg_option = st.selectbox("Select Time Aggregation", ["Daily", "Weekly", "Monthly"])
time_map = {
    "Daily": "DATE(ev.event_timestamp)",
    "Weekly": "DATE_TRUNC('week', ev.event_timestamp)",
    "Monthly": "DATE_TRUNC('month', ev.event_timestamp)"
}
time_column = time_map[agg_option]
query_time = q.USAGE_BY_PERIOD.format(time_column=time_column)
df_time = run_query(query_time)
if df_time.empty:
    st.warning("No data available.")
else:
    df_time["total_tokens"] = pd.to_numeric(df_time["total_tokens"], errors="coerce").fillna(0)
    plot_line(df_time, "period", "total_tokens", f"Token Usage Over Time ({agg_option})", xlabel="Time", ylabel="Total Tokens")

# Token Consumption by Level
st.header("Token Consumption by Level")
df_level = run_query(q.TOKEN_BY_LEVEL)
if df_level.empty:
    st.warning("No data available.")
else:
    df_level["level"] = df_level["level"].fillna("Unknown")
    df_level["total_tokens"] = pd.to_numeric(df_level["total_tokens"], errors="coerce").fillna(0)
    plot_bar(df_level, "level", "total_tokens", "Total Token Usage by Level", xlabel="Level", ylabel="Total Tokens", rotate=False)