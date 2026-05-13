import streamlit as st

from sidebar_logistica import sidebar_logistica

from alta_embarque_app import alta_embarque_app
from consulta_embarques_app import consulta_embarques_app
from actualizar_estatus_embarque_app import actualizar_estatus_embarque_app
from dashboard_embarques_app import dashboard_embarques_app


def logistica_app():

    menu_logistica, submenu_logistica, opcion_logistica = sidebar_logistica()

    if opcion_logistica is None:

        menu_logistica = "📦 Embarques"
        submenu_logistica = "Embarques"
        opcion_logistica = "➕ Alta embarque"

    st.title("🚚 Logística")

    st.divider()

    # =====================================================
    # ALTA EMBARQUE
    # =====================================================

    if opcion_logistica == "➕ Alta embarque":

        alta_embarque_app()

    elif opcion_logistica == "✏️ Actualizar estatus embarque":

        actualizar_estatus_embarque_app()

    
    # =====================================================
    # CONSULTA EMBARQUE
    # =====================================================

    elif opcion_logistica == "📋 Consulta embarque":

        consulta_embarques_app()

    elif opcion_logistica == "📊 Dashboard embarques":

        dashboard_embarques_app()
    # =====================================================
    # BAJA EMBARQUE
    # =====================================================

    elif opcion_logistica == "❌ Baja embarque":

        st.subheader("❌ Baja embarque")

        st.info("Módulo en construcción.")

    # =====================================================
    # DEFAULT
    # =====================================================

    else:

        st.subheader(opcion_logistica)

        st.info("Módulo de Logística en construcción.")

        st.write("Menú:", menu_logistica)
        st.write("Submenú:", submenu_logistica)
        st.write("Opción:", opcion_logistica)
