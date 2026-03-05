import psycopg2
import pandas as pd
import streamlit as st
from config import DB_CONFIG

@st.cache_resource
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@st.cache_data
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)