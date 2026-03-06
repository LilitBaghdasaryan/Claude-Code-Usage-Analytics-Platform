import psycopg2
import pandas as pd
import streamlit as st
from config import DB_CONFIG

@st.cache_resource
def get_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError as e:
        st.error(f"Could not connect to database: {e}")
        st.stop()

@st.cache_data
def run_query(query):
    try:
        conn = get_connection()
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()  # return empty df