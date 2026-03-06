import streamlit as st
import pandas as pd
from database import run_query
import queries as q
from utils import plot_bar

st.set_page_config(page_title="Cost Analysis")

st.header("Total Cost by Role")
df_cost = run_query(q.COST_BY_ROLE)
if df_cost.empty:
    st.warning("No data available.")
else:
    df_cost["practice"] = df_cost["practice"].fillna("Unknown")
    df_cost["total_cost"] = pd.to_numeric(df_cost["total_cost"], errors="coerce").fillna(0)
    plot_bar(df_cost, "practice", "total_cost", "Cost by User Role", xlabel="Role", ylabel="Total Cost ($)")