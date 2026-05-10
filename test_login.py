import streamlit as st
import pandas as pd
from database import get_connection


def diagnostico_bd_app():

    st.title("🔎 Diagnóstico Base de Datos")

    conn = get_connection()

    tablas_df = pd.read_sql_query(
        """
        SELECT name AS tabla
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """,
        conn
    )

    if tablas_df.empty:
        st.warning("No hay tablas en la base de datos.")
        conn.close()
        return

    tabla_sel = st.selectbox(
        "Selecciona tabla",
        tablas_df["tabla"].tolist()
    )

    st.markdown("### 📋 Estructura de la tabla")

    estructura_df = pd.read_sql_query(
        f"PRAGMA table_info({tabla_sel})",
        conn
    )

    st.dataframe(
        estructura_df,
        use_container_width=True
    )

    st.markdown("### 📊 Registros")

    total_df = pd.read_sql_query(
        f"SELECT COUNT(*) AS total FROM {tabla_sel}",
        conn
    )

    st.metric(
        "Total registros",
        int(total_df["total"].iloc[0])
    )

    limite = st.number_input(
        "Registros a mostrar",
        min_value=10,
        max_value=1000,
        value=100,
        step=10
    )

    datos_df = pd.read_sql_query(
        f"SELECT * FROM {tabla_sel} LIMIT {limite}",
        conn
    )

    st.dataframe(
        datos_df,
        use_container_width=True
    )

    conn.close()
