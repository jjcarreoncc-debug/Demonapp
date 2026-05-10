import sqlite3
import pandas as pd
import streamlit as st

conn = sqlite3.connect("erp.db")

df = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table'",
    conn
)

st.write(df)

conn.close()
