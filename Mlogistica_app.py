import streamlit as st

from sidebar_logistica import sidebar_logistica
from alta_embarque_app import alta_embarque_app


def logistica_app():

    menu_logistica, submenu_logistica, opcion_logistica = sidebar_logistica()

    if opcion_logistica is None:
        menu_logistica = "📦 Embarques"
        submenu_logistica = "Embarques"
        opcion_logistica = "➕ Alta embarque"

    st.title("🚚 Logística")

    st.divider()

    if opcion_logistica == "➕ Alta embarque":

        alta_embarque_app()

    else:

        st.subheader(opcion_logistica)

        st.info("Módulo de Logística en construcción.")

        st.write("Menú:", menu_logistica)
        st.write("Submenú:", submenu_logistica)
        st.write("Opción:", opcion_logistica)
