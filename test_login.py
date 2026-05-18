import streamlit as st
import sqlite3
import pandas as pd
import os


# =====================================================
# CONFIGURACION BLINDADA
# =====================================================

SEGURIDAD_DB_PATH = "/mount/src/demonapp/seguridad.db"


# =====================================================
# VALIDAR EXISTENCIA BASE
# =====================================================

def validar_base_seguridad():

    existe = os.path.exists(SEGURIDAD_DB_PATH)

    st.write("📂 Base configurada:")
    st.code(SEGURIDAD_DB_PATH)

    if existe:

        st.success("✅ seguridad.db existe")

        tamaño = os.path.getsize(SEGURIDAD_DB_PATH)

        st.write(f"📦 Tamaño archivo: {tamaño} bytes")

    else:

        st.error("❌ seguridad.db NO existe")


# =====================================================
# OBTENER TABLAS
# =====================================================

def obtener_tablas_seguridad():

    conn = sqlite3.connect(SEGURIDAD_DB_PATH)

    query = """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# =====================================================
# APP
# =====================================================

def validar_seguridad_db_app():

    st.title("🔒 Validación seguridad.db")

    st.warning(
        "Programa blindado exclusivamente a seguridad.db"
    )

    validar_base_seguridad()

    st.divider()

    st.subheader("📋 Tablas existentes")

    try:

        df_tablas = obtener_tablas_seguridad()

        if df_tablas.empty:

            st.warning(
                "⚠️ No existen tablas en seguridad.db"
            )

        else:

            st.success(
                f"✅ Se encontraron {len(df_tablas)} tabla(s)"
            )

            st.dataframe(
                df_tablas,
                use_container_width=True
            )

    except Exception as e:

        st.error(
            "❌ Error leyendo seguridad.db"
        )

        st.exception(e)


# =====================================================
# EJECUCION
# =====================================================

validar_seguridad_db_app()
