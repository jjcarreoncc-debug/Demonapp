import streamlit as st
import pandas as pd

from database import get_connection


st.title("🔎 CONSULTA TABLAS CON DATOS")

conn = get_connection()

tablas = [
    "usuarios",
    "roles",
    "modulos",
    "permisos_roles"
]

for tabla in tablas:

    st.markdown("---")
    st.subheader(f"📋 {tabla}")

    try:

        total_df = pd.read_sql_query(
            f"SELECT COUNT(*) AS total FROM {tabla}",
            conn
        )

        total = int(total_df["total"].iloc[0])

        st.metric(
            "Total registros",
            total
        )

        datos_df = pd.read_sql_query(
            f"SELECT * FROM {tabla}",
            conn
        )

        st.dataframe(
            datos_df,
            use_container_width=True
        )

    except Exception as e:

        st.error(f"Error leyendo {tabla}")
        st.exception(e)

conn.close()
