import streamlit as st

from sidebar_logistica import sidebar_logistica


def logistica_app():

    menu_logistica, submenu_logistica, opcion_logistica = sidebar_logistica()

    st.title("🚚 Logística")

    st.divider()

    st.subheader(opcion_logistica)

    st.info("Módulo de Logística en construcción.")

    st.write("Menú:", menu_logistica)
    st.write("Submenú:", submenu_logistica)
    st.write("Opción:", opcion_logistica)
