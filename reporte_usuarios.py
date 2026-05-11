import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "erp.db"


st.title("📊 Reporte de base ERP")

st.write("Ruta:")
st.code(str(DB_PATH))

st.write("Existe:")
st.write(DB_PATH.exists())

if DB_PATH.exists():
    st.write("Tamaño bytes:")
    st.write(DB_PATH.stat().st_size)

    conn = sqlite3.connect(DB_PATH)

    tablas = pd.read_sql_query("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """, conn)

    st.subheader("📋 Tablas")
    st.dataframe(tablas, use_container_width=True)

    for tabla in tablas["name"].tolist():
        st.markdown("---")
        st.subheader(f"📂 {tabla}")

        try:
            df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
            st.success(f"Registros: {len(df)}")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error leyendo {tabla}")
            st.exception(e)

    conn.close()
