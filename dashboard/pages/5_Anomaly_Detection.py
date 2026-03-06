from sklearn.ensemble import IsolationForest
import streamlit as st
import pandas as pd
from database import run_query
import queries as q

st.header("Anomaly Detection: Unusual Token Usage")

df_users = run_query(q.USER_DAILY_TOKENS)
if df_users.empty:
    st.warning("No data available.")
else:
    df_users["total_tokens"] = pd.to_numeric(df_users["total_tokens"], errors="coerce").fillna(0)
    df_users["day"] = pd.to_datetime(df_users["day"])

    model = IsolationForest(contamination=0.05, random_state=42)
    df_users["anomaly"] = model.fit_predict(df_users[["total_tokens"]])

    anomalies = df_users[df_users["anomaly"] == -1].copy()
    anomalies = anomalies[["user_name", "day", "total_tokens"]].sort_values("total_tokens", ascending=False)
    anomalies["day"] = anomalies["day"].dt.strftime("%Y-%m-%d")
    anomalies.columns = ["User", "Day", "Total Tokens"]

    st.markdown(f"**{len(anomalies)} anomalous days detected**")
    st.dataframe(anomalies, use_container_width=False)