import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "erp.db"


st.title("🧪 Diagnóstico ERP DB")

st.write("Ruta usada:")
st.code(str(DB_PATH))

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

st.subheader("📋 Tablas")

tablas = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
""").fetchall()

for t in tablas:
    st.write(dict(t))

st.markdown("---")

for tabla in [t["name"] for t in tablas]:
    st.subheader(f"Tabla: {tabla}")

    try:
        df = pd.read_sql_query(f"SELECT * FROM {tabla} LIMIT 10", conn)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.exception(e)

conn.close()
