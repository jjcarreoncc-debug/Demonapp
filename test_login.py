import streamlit as st
import pandas as pd
from database import get_connection


st.title("🔎 TEST BASE DE DATOS")

conn = get_connection()

tablas_df = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn
)

st.write("TABLAS ENCONTRADAS:")
st.dataframe(tablas_df)

if not tablas_df.empty:

    tabla = tablas_df.iloc[0]["name"]

    st.write("PRIMERA TABLA:", tabla)

    estructura_df = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    st.write("ESTRUCTURA:")
    st.dataframe(estructura_df)

    datos_df = pd.read_sql_query(
        f"SELECT * FROM {tabla} LIMIT 20",
        conn
    )

    st.write("DATOS:")
    st.dataframe(datos_df)

conn.close()
