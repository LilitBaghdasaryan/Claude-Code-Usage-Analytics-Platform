import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

@st.cache_data
def run_query(query):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("Claude Telemetry Analytics Dashboard")


# Token Consumption by Role
st.header("Token Consumption by User Role")

query_tokens = """
SELECT 
    u.practice,
    SUM(CAST(ev.input_tokens AS INTEGER)) AS total_input_tokens,
    SUM(CAST(ev.output_tokens AS INTEGER)) AS total_output_tokens,
    SUM(CAST(ev.input_tokens AS INTEGER) + CAST(ev.output_tokens AS INTEGER)) AS total_tokens
FROM events ev
JOIN sessions s ON ev.session_id = s.session_id
JOIN users u ON s.user_id = u.user_id
GROUP BY u.practice
ORDER BY total_tokens DESC;
"""

df_tokens = run_query(query_tokens)
df_tokens["practice"] = df_tokens["practice"].fillna("Unknown")
df_tokens["total_tokens"] = pd.to_numeric(df_tokens["total_tokens"], errors="coerce").fillna(0)

st.dataframe(df_tokens)

fig1, ax1 = plt.subplots()
ax1.bar(df_tokens["practice"], df_tokens["total_tokens"])
ax1.set_xlabel("Role")
ax1.set_ylabel("Total Tokens")
ax1.set_title("Total Token Usage by Role")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig1)

st.header("Token Consumption Share by Role (Pie Chart)")

fig_pie2, ax_pie2 = plt.subplots()
ax_pie2.pie(df_tokens["total_tokens"], labels=df_tokens["practice"], autopct='%1.1f%%', startangle=140)
ax_pie2.set_title("Token Usage Share by Role")
st.pyplot(fig_pie2)

# Peak Usage Times
st.header("Peak Usage Times")

# Hourly
query_hour = """
SELECT 
    EXTRACT(HOUR FROM ev.event_timestamp) AS hour,
    COUNT(*) AS total_events
FROM events ev
GROUP BY hour
ORDER BY hour;
"""
df_hour = run_query(query_hour)
fig2, ax2 = plt.subplots()
ax2.plot(df_hour["hour"], df_hour["total_events"], marker='o')
ax2.set_xlabel("Hour of Day")
ax2.set_ylabel("Number of Events")
ax2.set_title("Usage by Hour")
st.pyplot(fig2)

st.header("Token Usage Over Time")

# Aggregation level selectbox
agg_option = st.selectbox(
    "Select Time Aggregation",
    ["Daily", "Weekly", "Monthly"]
)

if agg_option == "Daily":
    time_column = "DATE(ev.event_timestamp)"
elif agg_option == "Weekly":
    time_column = "DATE_TRUNC('week', ev.event_timestamp)"
elif agg_option == "Monthly":
    time_column = "DATE_TRUNC('month', ev.event_timestamp)"

query_time = f"""
SELECT 
    {time_column} AS period,
    SUM(CAST(ev.input_tokens AS INTEGER) + CAST(ev.output_tokens AS INTEGER)) AS total_tokens
FROM events ev
GROUP BY period
ORDER BY period;
"""

df_time = run_query(query_time)
df_time["total_tokens"] = pd.to_numeric(df_time["total_tokens"], errors="coerce").fillna(0)

fig_time, ax_time = plt.subplots()
ax_time.plot(df_time["period"], df_time["total_tokens"], marker='o')
ax_time.set_xlabel("Time")
ax_time.set_ylabel("Total Tokens")
ax_time.set_title(f"Token Usage Over Time ({agg_option})")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig_time)

# Event Type Distribution
st.header("Most Common Event Types")

query_events = """
SELECT 
    event_type,
    COUNT(*) AS frequency
FROM events
GROUP BY event_type
ORDER BY frequency DESC;
"""
df_events = run_query(query_events)
df_events["event_type"] = df_events["event_type"].fillna("Unknown")
st.dataframe(df_events)

fig4, ax4 = plt.subplots()
ax4.bar(df_events["event_type"], df_events["frequency"])
ax4.set_xlabel("Frequency")
ax4.set_title("Event Type Distribution")
st.pyplot(fig4)

st.header("Event Type Share (Pie Chart)")

fig_pie1, ax_pie1 = plt.subplots()
ax_pie1.pie(df_events["frequency"], labels=df_events["event_type"], autopct='%1.1f%%', startangle=140)
ax_pie1.set_title("Event Type Distribution")
st.pyplot(fig_pie1)

# Cost by Role
st.header("Total Cost by User Role")

query_cost = """
SELECT 
    u.practice,
    SUM(CAST(ev.cost_usd AS FLOAT)) AS total_cost
FROM events ev
JOIN sessions s ON ev.session_id = s.session_id
JOIN users u ON s.user_id = u.user_id
GROUP BY u.practice
ORDER BY total_cost DESC;
"""
df_cost = run_query(query_cost)
df_cost["practice"] = df_cost["practice"].fillna("Unknown")
df_cost["total_cost"] = pd.to_numeric(df_cost["total_cost"], errors="coerce").fillna(0)
st.dataframe(df_cost)

fig5, ax5 = plt.subplots()
ax5.bar(df_cost["practice"], df_cost["total_cost"])
ax5.set_xlabel("Role")
ax5.set_ylabel("Total Cost ($)")
ax5.set_title("Cost by User Role")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig5)

# Tool Acceptance / Rejection Rate
st.header("Tool Acceptance vs Rejection")

query_tool = """
SELECT 
    tool_name,
    decision,
    COUNT(*) AS count
FROM events
WHERE event_type='tool_decision'
GROUP BY tool_name, decision
ORDER BY tool_name;
"""
df_tool = run_query(query_tool)
st.dataframe(df_tool)

# Pivot for stacked bar
df_tool_pivot = df_tool.pivot(index='tool_name', columns='decision', values='count').fillna(0)
fig6, ax6 = plt.subplots()
df_tool_pivot.plot(kind='bar', stacked=True, ax=ax6)
ax6.set_ylabel("Count")
ax6.set_title("Tool Decisions")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig6)


# Average Prompt Length by Role
st.header("Average Prompt Length by Role")

query_prompt = """
SELECT 
    u.practice,
    AVG(CAST(ev.prompt_length AS INTEGER)) AS avg_prompt_length
FROM events ev
JOIN sessions s ON ev.session_id = s.session_id
JOIN users u ON s.user_id = u.user_id
WHERE ev.prompt_length IS NOT NULL
GROUP BY u.practice
ORDER BY avg_prompt_length DESC;
"""
df_prompt = run_query(query_prompt)
df_prompt["practice"] = df_prompt["practice"].fillna("Unknown")
df_prompt["avg_prompt_length"] = pd.to_numeric(df_prompt["avg_prompt_length"], errors="coerce").fillna(0)
st.dataframe(df_prompt)

fig7, ax7 = plt.subplots()
ax7.bar(df_prompt["practice"], df_prompt["avg_prompt_length"])
ax7.set_xlabel("Role")
ax7.set_ylabel("Average Prompt Length")
ax7.set_title("Average Prompt Length by Role")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig7)

# Power Users (Top / Bottom)
st.header("Power Users by Token Usage")

# User selects top or bottom
rank_option = st.selectbox(
    "Show",
    ["Top 10 Users", "Bottom 10 Users"]
)

order = "DESC" if "Top" in rank_option else "ASC"

query_users = f"""
SELECT 
    s.user_id,
    u.full_name AS user_name,
    SUM(CAST(ev.input_tokens AS INTEGER) + CAST(ev.output_tokens AS INTEGER)) AS total_tokens
FROM events ev
JOIN sessions s ON ev.session_id = s.session_id
JOIN users u ON s.user_id = u.user_id
GROUP BY s.user_id, u.full_name
ORDER BY total_tokens {order}
LIMIT 10;
"""

df_users = run_query(query_users)
df_users["total_tokens"] = pd.to_numeric(df_users["total_tokens"], errors="coerce").fillna(0)

st.dataframe(df_users)

# Bar chart
fig8, ax8 = plt.subplots()
ax8.bar(df_users["user_name"], df_users["total_tokens"])
ax8.set_xlabel("Total Tokens")
ax8.set_ylabel("User")
ax8.set_title(rank_option)
plt.xticks(rotation=45, ha="right")
st.pyplot(fig8)
