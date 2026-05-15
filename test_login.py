import sqlite3
import pandas as pd
import streamlit as st

from sigem_db import get_db_path


def obtener_tablas(conn):

    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """

    return pd.read_sql_query(query, conn)


def obtener_columnas(conn, tabla):

    query = f"""
        PRAGMA table_info({tabla})
    """

    return pd.read_sql_query(query, conn)


def test_estructura_db_app():

    st.markdown("## 🧪 Test estructura de base de datos")
    st.caption("Revisa tablas, columnas y posibles diferencias de estructura.")

    bases = [
        "erp",
        "inventarios",
        "materiales",
        "compras",
        "logistica",
        "wms"
    ]

    base_sel = st.selectbox(
        "Selecciona base de datos",
        bases
    )

    try:

        db_path = get_db_path(base_sel)

        st.info(f"📁 Base seleccionada: {db_path}")

        conn = sqlite3.connect(db_path)

        tablas_df = obtener_tablas(conn)

        if tablas_df.empty:

            st.warning("⚠️ No se encontraron tablas en esta base.")
            conn.close()
            return

        st.markdown("### 📋 Tablas encontradas")

        st.dataframe(
            tablas_df,
            use_container_width=True
        )

        tabla_sel = st.selectbox(
            "Selecciona tabla para revisar columnas",
            tablas_df["name"].tolist()
        )

        columnas_df = obtener_columnas(conn, tabla_sel)

        st.markdown(f"### 🧱 Columnas de tabla: `{tabla_sel}`")

        st.dataframe(
            columnas_df,
            use_container_width=True
        )

        st.markdown("### 🔎 Validación rápida usuarios / roles")

        if tabla_sel == "usuarios":

            columnas = columnas_df["name"].tolist()

            requeridas = [
                "id_usuario",
                "usuario",
                "nombre",
                "email",
                "password_hash",
                "id_rol",
                "estado",
                "modulo_inicial",
                "fecha_creacion",
                "ultimo_login"
            ]

            faltantes = [
                col
                for col in requeridas
                if col not in columnas
            ]

            if faltantes:

                st.error("❌ Columnas faltantes en usuarios:")

                st.write(faltantes)

            else:

                st.success("✅ La tabla usuarios tiene las columnas principales.")

        if tabla_sel == "roles":

            columnas = columnas_df["name"].tolist()

            requeridas = [
                "id_rol",
                "nombre_rol",
                "descripcion",
                "estado",
                "fecha_creacion"
            ]

            faltantes = [
                col
                for col in requeridas
                if col not in columnas
            ]

            if faltantes:

                st.error("❌ Columnas faltantes en roles:")

                st.write(faltantes)

            else:

                st.success("✅ La tabla roles tiene las columnas principales.")

        conn.close()

    except Exception as e:

        st.error("❌ Error revisando estructura de base de datos.")
        st.exception(e)


if __name__ == "__main__":

    test_estructura_db_app()
