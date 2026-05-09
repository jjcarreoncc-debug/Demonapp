import streamlit as st
import pandas as pd

from database import get_connection


st.title("🧪 Test Base de Datos")

conn = get_connection()
cursor = conn.cursor()

st.subheader("📋 Tablas existentes")

tablas = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn
)

st.dataframe(tablas, use_container_width=True)

st.subheader("🧱 Estructura tabla modulos")

try:
    estructura_modulos = pd.read_sql_query(
        "PRAGMA table_info(modulos)",
        conn
    )
    st.dataframe(estructura_modulos, use_container_width=True)
except Exception as e:
    st.error("No se pudo leer estructura de modulos")
    st.exception(e)

st.subheader("📦 Datos tabla modulos")

try:
    modulos = pd.read_sql_query(
        "SELECT * FROM modulos",
        conn
    )
    st.dataframe(modulos, use_container_width=True)
except Exception as e:
    st.error("No se pudo leer tabla modulos")
    st.exception(e)

st.subheader("🔐 Estructura tabla permisos_roles")

try:
    estructura_permisos = pd.read_sql_query(
        "PRAGMA table_info(permisos_roles)",
        conn
    )
    st.dataframe(estructura_permisos, use_container_width=True)
except Exception as e:
    st.error("No se pudo leer estructura de permisos_roles")
    st.exception(e)

st.subheader("🔑 Datos tabla permisos_roles")

try:
    permisos = pd.read_sql_query(
        "SELECT * FROM permisos_roles",
        conn
    )
    st.dataframe(permisos, use_container_width=True)
except Exception as e:
    st.error("No se pudo leer tabla permisos_roles")
    st.exception(e)

conn.close()
