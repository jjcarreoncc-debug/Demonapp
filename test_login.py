import streamlit as st
import pandas as pd

from database import get_connection


st.title("🔎 VER TABLAS DISPONIBLES")

conn = get_connection()

tablas_df = pd.read_sql_query(
    """
    SELECT name AS tabla
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn
)

st.dataframe(
    tablas_df,
    use_container_width=True
)

conn.close()
