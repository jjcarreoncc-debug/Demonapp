import streamlit as st

from compras_db import crear_tablas_compras


def crear_tablas_app():

    st.title("🗄️ Crear tablas")

    modulo = st.selectbox(
        "Selecciona módulo",
        [
            "Compras"
        ],
        key="crear_tablas_modulo"
    )

    st.info(
        "Este proceso crea las tablas base del módulo seleccionado si no existen."
    )

    if st.button("🚀 Crear tablas", key="btn_crear_tablas"):

        try:

            if modulo == "Compras":
                crear_tablas_compras()

            st.success(
                f"✅ Tablas del módulo {modulo} creadas correctamente"
            )

        except Exception as e:

            st.error(
                f"❌ Error creando tablas del módulo {modulo}"
            )

            st.exception(e)
