import streamlit as st
import pandas as pd
from database import get_connection


st.title("🔎 TEST TABLAS BASE DE DATOS")

conn = get_connection()

# ==========================================
# LISTAR TABLAS
# ==========================================

tablas_df = pd.read_sql_query(
    """
    SELECT name AS tabla
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn
)

st.subheader("📋 Tablas encontradas")

st.dataframe(
    tablas_df,
    use_container_width=True
)

# ==========================================
# SELECCIONAR TABLA
# ==========================================

if not tablas_df.empty:

    tabla_sel = st.selectbox(
        "Selecciona tabla",
        tablas_df["tabla"].tolist()
    )

    # ==========================================
    # ESTRUCTURA
    # ==========================================

    st.subheader("📘 Estructura tabla")

    estructura_df = pd.read_sql_query(
        f"PRAGMA table_info({tabla_sel})",
        conn
    )

    st.dataframe(
        estructura_df,
        use_container_width=True
    )

    # ==========================================
    # TOTAL REGISTROS
    # ==========================================

    total_df = pd.read_sql_query(
        f"SELECT COUNT(*) AS total FROM {tabla_sel}",
        conn
    )

    total = int(total_df["total"].iloc[0])

    st.metric(
        "Total registros",
        total
    )

    # ==========================================
    # DATOS
    # ==========================================

    if total > 0:

        st.subheader("📊 Datos")

        datos_df = pd.read_sql_query(
            f"SELECT * FROM {tabla_sel} LIMIT 100",
            conn
        )

        st.dataframe(
            datos_df,
            use_container_width=True
        )

    else:

        st.warning("⚠️ Tabla vacía")

conn.close()
