import streamlit as st

from sidebar_logistica import sidebar_logistica

from alta_embarque_app import alta_embarque_app
from consulta_embarques_app import consulta_embarques_app
from actualizar_estatus_embarque_app import actualizar_estatus_embarque_app
from dashboard_embarques_app import dashboard_embarques_app


def logistica_app():

    # =====================================================
    # SESSION STATE
    # =====================================================

    if "opcion_logistica" not in st.session_state:

        st.session_state.opcion_logistica = "➕ Alta embarque"

    # =====================================================
    # SIDEBAR
    # =====================================================

    menu_logistica, submenu_logistica, opcion_logistica = sidebar_logistica()

    # =====================================================
    # CONSERVAR OPCION
    # =====================================================

    if opcion_logistica is not None:

        st.session_state.opcion_logistica = opcion_logistica

    opcion_logistica = st.session_state.opcion_logistica

    # =====================================================
    # TITULO
    # =====================================================

    st.title("🚚 Logística")

    st.divider()

    # =====================================================
    # ALTA EMBARQUE
    # =====================================================

    if opcion_logistica == "➕ Alta embarque":

        alta_embarque_app()

    # =====================================================
    # ACTUALIZAR ESTATUS
    # =====================================================

    elif opcion_logistica == "✏️ Actualizar estatus embarque":

        actualizar_estatus_embarque_app()

    # =====================================================
    # CONSULTA EMBARQUE
    # =====================================================

    elif opcion_logistica == "📋 Consulta embarque":

        consulta_embarques_app()

    # =====================================================
    # DASHBOARD
    # =====================================================

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
