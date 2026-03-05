import streamlit as st
import pandas as pd
from database import run_query
from utils import plot_bar
import queries as q

st.set_page_config(page_title="User Analysis")

# Average Prompt Length
st.header("Average Prompt Length by Role")
df_prompt = run_query(q.PROMPT_LENGTH_BY_ROLE)
df_prompt["practice"] = df_prompt["practice"].fillna("Unknown")
df_prompt["avg_prompt_length"] = pd.to_numeric(df_prompt["avg_prompt_length"], errors="coerce").fillna(0)
plot_bar(df_prompt, "practice", "avg_prompt_length", "Average Prompt Length by Role", xlabel="Role", ylabel="Average Prompt Length")

# Power Users
st.header("Power Users by Token Usage")
rank_option = st.selectbox("Show", ["Top 10 Users", "Bottom 10 Users"])
order = "DESC" if "Top" in rank_option else "ASC"
query_users = q.TOP_BOTTOM_USERS.format(order=order)
df_users = run_query(query_users)
df_users["total_tokens"] = pd.to_numeric(df_users["total_tokens"], errors="coerce").fillna(0)
st.dataframe(df_users.drop(columns="user_id"))
plot_bar(df_users, "user_name", "total_tokens", rank_option, xlabel="User", ylabel="Total Tokens")
