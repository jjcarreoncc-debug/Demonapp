import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

from sigem_db import DB_CONFIG, get_db_path


def obtener_tamano_kb(db_path):

    try:
        path = Path(db_path)

        if path.exists():
            return round(path.stat().st_size / 1024, 2)

        return 0

    except:
        return 0


def obtener_tablas(conn):

    query = """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """

    df = pd.read_sql_query(query, conn)

    return df["name"].tolist()


def revisar_estructura_db_app():

    st.title("🔍 Revisar estructura DB")

    st.caption("Configuración / Revisar estructura DB")

    bases_disponibles = list(DB_CONFIG.keys())

    base_seleccionada = st.selectbox(
        "Selecciona base de datos",
        bases_disponibles
    )

    db_path = get_db_path(base_seleccionada)

    st.subheader("📂 Información base")

    c1, c2 = st.columns(2)

    with c1:
        st.write("Base:")
        st.code(base_seleccionada)

    with c2:
        st.write("Tamaño KB:")
        st.code(str(obtener_tamano_kb(db_path)))

    st.write("Ruta:")
    st.code(str(db_path))

    try:

        conn = sqlite3.connect(db_path)

        tablas = obtener_tablas(conn)

        tablas = sorted(tablas)

        if "inventario_fisico" not in tablas:
            tablas.append("inventario_fisico")

        if "ajustes_inventario" not in tablas:
            tablas.append("ajustes_inventario")

        if not tablas:

            st.warning("Esta base no tiene tablas.")
            conn.close()
            return

        st.subheader("📋 Tablas disponibles")

        tabla_seleccionada = st.selectbox(
            "Selecciona tabla",
            tablas
        )

        st.subheader("🧱 Estructura tabla")

        df_estructura = pd.read_sql_query(
            f"PRAGMA table_info({tabla_seleccionada})",
            conn
        )

        st.dataframe(
            df_estructura,
            use_container_width=True
        )

        st.subheader("📊 Resumen tabla")

        total_registros = pd.read_sql_query(
            f"SELECT COUNT(*) AS total FROM {tabla_seleccionada}",
            conn
        )["total"].iloc[0]

        st.metric(
            "Registros",
            total_registros
        )

        st.subheader("📦 Últimos registros")

        df_datos = pd.read_sql_query(
            f"SELECT * FROM {tabla_seleccionada} LIMIT 50",
            conn
        )

        st.dataframe(
            df_datos,
            use_container_width=True
        )

        conn.close()

    except Exception as e:

        st.error("Error revisando estructura de la base.")
        st.exception(e)


if __name__ == "__main__":
    revisar_estructura_db_app()
