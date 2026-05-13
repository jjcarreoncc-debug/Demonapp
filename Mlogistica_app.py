import streamlit as st

from sidebar_logistica import sidebar_logistica
from alta_embarque_app import alta_embarque_app


def logistica_app():

    menu_logistica, submenu_logistica, opcion_logistica = sidebar_logistica()

    st.title("🚚 Logística")

    st.divider()

menu_logistica, submenu_logistica, opcion_logistica = sidebar_logistica()

if opcion_logistica is None:
    opcion_logistica = "➕ Alta embarque"


if opcion_logistica == "➕ Alta embarque":

    alta_embarque_app()

else:

    st.subheader(opcion_logistica)

    st.info("Módulo de Logística en construcción.")

    st.write("Menú:", menu_logistica)
    st.write("Submenú:", submenu_logistica)
    st.write("Opción:", opcion_logistica)

        st.subheader(opcion_logistica)

        st.info("Módulo de Logística en construcción.")

        st.write("Menú:", menu_logistica)
        st.write("Submenú:", submenu_logistica)
        st.write("Opción:", opcion_logistica)
