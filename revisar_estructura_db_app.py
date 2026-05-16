import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

from sigem_db import DB_CONFIG, get_db_path


# =========================================================
# TAMAÑO DB
# =========================================================

def obtener_tamano_kb(db_path):

    try:

        path = Path(db_path)

        if path.exists():
            return round(path.stat().st_size / 1024, 2)

        return 0

    except:
        return 0


# =========================================================
# OBTENER TABLAS REALES
# =========================================================

def obtener_tablas(conn):

    query = """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """

    df = pd.read_sql_query(query, conn)

    return df["name"].tolist()


# =========================================================
# TABLAS POR MODULO
# =========================================================

TABLAS_MODULOS = {

    "Seguridad": [
        "usuarios",
        "roles",
        "permisos",
        "modulos",
        "usuario_roles",
        "rol_permisos",
        "sesiones_usuario"
    ],

    "Inventarios": [
        "materiales",
        "movimientos_inventario",
        "inventario_fisico",
        "ajustes_inventario"
    ],

    "Compras": [
        "proveedores",
        "ordenes_compra",
        "detalle_orden_compra",
        "recepciones_compra"
    ],
    #
    "Logística": [

        "clientes",
    
        "pedidos",
    
        "detalle_pedido",
    
        "hoja_carga",
    
        "detalle_hoja_carga",
    
        "embarques",
    
        "detalle_embarque",
    
        "transportes",
    
        "rutas",
    
        "puntos_ruta",
    
        "eventos_embarque"
    ],
    #
    "WMS": [
        "ubicaciones_wms",
        "movimientos_wms"
    ]
}


# =========================================================
# APP
# =========================================================

def revisar_estructura_db_app():

    st.title("🔍 Revisar estructura DB")

    st.caption(
        "Configuración / Revisar estructura DB"
    )

    # =====================================================
    # BASES
    # =====================================================

    bases_disponibles = list(DB_CONFIG.keys())

    base_seleccionada = st.selectbox(
        "Selecciona base de datos",
        bases_disponibles
    )

    db_path = get_db_path(base_seleccionada)

    # =====================================================
    # INFO DB
    # =====================================================

    st.subheader("📂 Información base")

    c1, c2 = st.columns(2)

    with c1:

        st.write("Base:")
        st.code(base_seleccionada)

    with c2:

        st.write("Tamaño KB:")
        st.code(
            str(
                obtener_tamano_kb(db_path)
            )
        )

    st.write("Ruta:")
    st.code(str(db_path))

    # =====================================================
    # CONEXION
    # =====================================================

    try:

        conn = sqlite3.connect(db_path)

        tablas_reales = obtener_tablas(conn)

        tablas_reales = sorted(tablas_reales)

        # =================================================
        # MODULO
        # =================================================

        st.subheader("🧩 Selección módulo")

        modulos_disponibles = list(
            TABLAS_MODULOS.keys()
        )

        modulo_seleccionado = st.selectbox(
            "Selecciona módulo",
            modulos_disponibles
        )

        tablas_modulo = TABLAS_MODULOS.get(
            modulo_seleccionado,
            []
        )

        tablas_visualizar = []

        # =================================================
        # VALIDAR EXISTENCIA
        # =================================================

        for tabla in tablas_modulo:

            if tabla in tablas_reales:

                tablas_visualizar.append(tabla)

            else:

                tablas_visualizar.append(
                    f"❌ {tabla}"
                )

        tablas_visualizar = sorted(
            tablas_visualizar
        )

        # =================================================
        # TABLAS DISPONIBLES
        # =================================================

        st.subheader("📋 Tablas disponibles")

        tabla_seleccionada = st.selectbox(
            "Selecciona tabla",
            tablas_visualizar
        )

        # =================================================
        # TABLA NO EXISTE
        # =================================================

        if tabla_seleccionada.startswith("❌"):

            tabla_real = (
                tabla_seleccionada
                .replace("❌", "")
                .strip()
            )

            st.error(
                f"La tabla '{tabla_real}' "
                f"no existe."
            )

            st.info(
                "Debe incluirse en el "
                "proceso de Crear tablas."
            )

            conn.close()
            return

        # =================================================
        # ESTRUCTURA
        # =================================================

        st.subheader("🧱 Estructura tabla")

        df_estructura = pd.read_sql_query(
            f"PRAGMA table_info({tabla_seleccionada})",
            conn
        )

        st.dataframe(
            df_estructura,
            use_container_width=True
        )

        # =================================================
        # TOTAL REGISTROS
        # =================================================

        st.subheader("📊 Resumen tabla")

        total_registros = pd.read_sql_query(
            f"""
            SELECT COUNT(*) AS total
            FROM {tabla_seleccionada}
            """,
            conn
        )["total"].iloc[0]

        st.metric(
            "Registros",
            total_registros
        )

        # =================================================
        # ULTIMOS REGISTROS
        # =================================================

        st.subheader("📦 Últimos registros")

        df_datos = pd.read_sql_query(
            f"""
            SELECT *
            FROM {tabla_seleccionada}
            LIMIT 50
            """,
            conn
        )

        st.dataframe(
            df_datos,
            use_container_width=True
        )

        conn.close()

    except Exception as e:

        st.error(
            "Error revisando estructura de la base."
        )

        st.exception(e)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    revisar_estructura_db_app()
