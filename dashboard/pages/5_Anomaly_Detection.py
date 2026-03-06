from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import run_query
import queries as q

st.header("Anomaly Detection: Unusual Token Usage")

st.caption(
    "Identifies days with unusual patterns in token usage, event count, duration, cost, and sessions using Isolation Forest. "
    "Anomalies may indicate spikes, testing, or outliers worth reviewing."
)

MIN_SAMPLES = 10
df_users = run_query(q.USER_DAILY_TOKENS)

if df_users.empty:
    st.warning("No data available.")
else:
    features = ["total_tokens", "event_count", "avg_duration_ms", "avg_cost_usd", "session_count"]
    for col in features:
        df_users[col] = pd.to_numeric(df_users[col], errors="coerce").fillna(0)
    df_users["day"] = pd.to_datetime(df_users["day"])

    if len(df_users) < MIN_SAMPLES:
        st.warning(f"Need at least {MIN_SAMPLES} daily records for anomaly detection. Found {len(df_users)}.")
    else:
        contamination = st.slider(
            "Expected proportion of anomalies",
            min_value=0.01,
            max_value=0.20,
            value=0.05,
            step=0.01,
            help="Rough share of points to label as anomalies (e.g. 0.05 = 5%).",
        )

        X = df_users[features].copy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = IsolationForest(contamination=contamination, random_state=42)
        df_users["anomaly"] = model.fit_predict(X_scaled)

        anomalies = df_users[df_users["anomaly"] == -1].copy()
        anomalies = anomalies[
            ["user_name", "day", "total_tokens", "event_count", "avg_duration_ms", "avg_cost_usd", "session_count"]
        ]
        anomalies = anomalies.sort_values("total_tokens", ascending=False)
        anomalies_display = anomalies.copy()
        anomalies_display["day"] = anomalies_display["day"].dt.strftime("%Y-%m-%d")
        anomalies_display["avg_duration_ms"] = anomalies_display["avg_duration_ms"].round(1)
        anomalies_display["avg_cost_usd"] = anomalies_display["avg_cost_usd"].round(4)
        anomalies_display.columns = [
            "User", "Day", "Total Tokens", "Event Count", "Avg Duration (ms)", "Avg Cost ($)", "Sessions"
        ]

        st.markdown(f"{len(anomalies)} anomalous days detected")
        st.dataframe(anomalies_display, use_container_width=True)

        st.subheader("Token usage over time (anomalies highlighted)")
        df_plot = df_users.copy()
        df_plot["day_str"] = df_plot["day"].dt.strftime("%Y-%m-%d")
        normal = df_plot[df_plot["anomaly"] == 1]
        anomalous = df_plot[df_plot["anomaly"] == -1]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.scatter(
            normal["day"],
            normal["total_tokens"],
            c="steelblue",
            alpha=0.6,
            s=30,
            label="Normal",
        )
        ax.scatter(
            anomalous["day"],
            anomalous["total_tokens"],
            c="coral",
            alpha=0.9,
            s=50,
            label="Anomaly",
            edgecolors="darkred",
        )
        ax.set_xlabel("Day")
        ax.set_ylabel("Total Tokens")
        ax.set_title("Daily token usage by user-day (anomalies in orange)")
        ax.legend()
        ax.tick_params(axis="x", rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)