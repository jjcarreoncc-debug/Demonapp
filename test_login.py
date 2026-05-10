import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("erp.db")

st.subheader("Columnas usuarios")
st.dataframe(pd.read_sql_query("PRAGMA table_info(usuarios)", conn))

st.subheader("Columnas roles")
st.dataframe(pd.read_sql_query("PRAGMA table_info(roles)", conn))

conn.close()
