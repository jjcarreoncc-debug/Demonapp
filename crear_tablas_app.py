import streamlit as st

from compras_db import crear_tablas_compras
from inventario_db import crear_tablas_inventario
from inventario_db import crear_tabla_movimientos_inventario


def crear_tablas_app():

    st.title("🗄️ Crear tablas")

    modulo = st.selectbox(
        "Selecciona módulo",
        [
            "Compras",
            "Inventarios"
        ],
        key="crear_tablas_modulo"
    )

    # ==========================================
    # TABLAS DISPONIBLES POR MÓDULO
    # ==========================================

    tablas_disponibles = []

    if modulo == "Compras":

        tablas_disponibles = [
            "Todas",
            "entradas_compras",
            "entradas_compras_detalle"
        ]

    elif modulo == "Inventarios":

        tablas_disponibles = [
            "Todas",
            "materiales",
            "movimientos_inventario"
        ]

    tabla = st.selectbox(
        "Selecciona tabla",
        tablas_disponibles,
        key="crear_tablas_tabla"
    )

    st.info(
        "Este proceso crea únicamente la tabla seleccionada si no existe."
    )

    # ==========================================
    # CREAR TABLAS
    # ==========================================

    if st.button("🚀 Crear tablas", key="btn_crear_tablas"):

        try:

            # ==================================
            # COMPRAS
            # ==================================

            if modulo == "Compras":

                if tabla == "Todas":

                    crear_tablas_compras()

                elif tabla == "entradas_compras":

                    crear_tablas_compras()

                elif tabla == "entradas_compras_detalle":

                    crear_tablas_compras()

            # ==================================
            # INVENTARIOS
            # ==================================

            elif modulo == "Inventarios":

                if tabla == "Todas":

                    crear_tablas_inventario()
                    crear_tabla_movimientos_inventario()

                elif tabla == "materiales":

                    crear_tablas_inventario()

                elif tabla == "movimientos_inventario":

                    crear_tabla_movimientos_inventario()

            st.success(
                f"✅ Tabla(s) creadas correctamente para {modulo}"
            )

        except Exception as e:

            st.error(
                f"❌ Error creando tablas del módulo {modulo}"
            )

            st.exception(e)
