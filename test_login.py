import streamlit as st
import pandas as pd
from database import get_connection

st.title("🔎 TEST estructura BD")

conn = get_connection()

tablas = [
    "usuarios",
    "roles",
    "modulos",
    "permisos_roles"
]

for tabla in tablas:

    st.subheader(f"📋 {tabla}")

    estructura = pd.read_sql_query(
        f"PRAGMA table_info({tabla})",
        conn
    )

    st.write("Estructura")
    st.dataframe(
        estructura,
        use_container_width=True
    )

    datos = pd.read_sql_query(
        f"SELECT * FROM {tabla} LIMIT 50",
        conn
    )

    st.write("Datos")
    st.dataframe(
        datos,
        use_container_width=True
    )

conn.close()
