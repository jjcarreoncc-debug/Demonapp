import streamlit as st
import sqlite3
import pandas as pd
import os


SEGURIDAD_DB_PATH = "/mount/src/demonapp/seguridad.db"
ERP_DB_PATH = "/mount/src/demonapp/erp.db"


def obtener_info_base(db_path):

    existe = os.path.exists(db_path)

    if not existe:
        return False, 0, pd.DataFrame(columns=["name"])

    tamaño = os.path.getsize(db_path)

    conn = sqlite3.connect(db_path)

    df_tablas = pd.read_sql_query("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """, conn)

    conn.close()

    return True, tamaño, df_tablas


def mostrar_base(nombre, db_path):

    st.subheader(nombre)

    st.write("📂 Ruta:")
    st.code(db_path)

    try:
        existe, tamaño, df_tablas = obtener_info_base(db_path)

        if not existe:
            st.error("❌ La base no existe")
            return

        st.success("✅ La base existe")
        st.write(f"📦 Tamaño: {tamaño} bytes")

        if df_tablas.empty:
            st.warning("⚠️ No tiene tablas")
        else:
            st.success(f"✅ Tiene {len(df_tablas)} tabla(s)")
            st.dataframe(df_tablas, use_container_width=True)

    except Exception as e:
        st.error("❌ Error leyendo la base")
        st.exception(e)


def validar_bases_seguridad_app():

    st.title("🔎 Comparar seguridad.db vs erp.db")

    st.warning(
        "Este programa solo consulta las bases. No crea, no borra y no modifica."
    )

    col1, col2 = st.columns(2)

    with col1:
        mostrar_base(
            "🔒 seguridad.db",
            SEGURIDAD_DB_PATH
        )

    with col2:
        mostrar_base(
            "🏢 erp.db",
            ERP_DB_PATH
        )


validar_bases_seguridad_app()
