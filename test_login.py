import streamlit as st
import pandas as pd

from database import get_connection

st.title("🔎 Verificar BD real")

conn = get_connection()

tablas = pd.read_sql_query(
    """
    SELECT name AS tabla
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn
)

st.dataframe(tablas, use_container_width=True)

conn.close()
