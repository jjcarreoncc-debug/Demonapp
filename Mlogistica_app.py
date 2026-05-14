import streamlit as st

from sidebar_logistica import sidebar_logistica

from alta_embarque_app import alta_embarque_app
from consulta_embarques_app import consulta_embarques_app
from actualizar_estatus_embarque_app import actualizar_estatus_embarque_app
from dashboard_embarques_app import dashboard_embarques_app
from eventos_embarque_app import eventos_embarque_app

# =====================================================
# INCIDENCIAS
# =====================================================

try:
    from alta_incidencia_app import alta_incidencia_app
except Exception:
    def alta_incidencia_app():
        st.subheader("➕ Alta incidencia")
        st.info("Módulo en construcción.")

try:
    from baja_incidencia_app import baja_incidencia_app
except Exception:
    def baja_incidencia_app():
        st.subheader("❌ Baja incidencia")
        st.info("Módulo en construcción.")

try:
    from consulta_incidencia_app import consulta_incidencia_app
except Exception:
    def consulta_incidencia_app():
        st.subheader("📋 Consulta incidencia")
        st.info("Módulo en construcción.")

try:
    from actualizar_incidencia_app import actualizar_incidencia_app
except Exception:
    def actualizar_incidencia_app():
        st.subheader("✏️ Actualizar incidencia")
        st.info("Módulo en construcción.")

try:
    from cerrar_incidencia_app import cerrar_incidencia_app
except Exception:
    def cerrar_incidencia_app():
        st.subheader("✅ Cerrar incidencia")
        st.info("Módulo en construcción.")

try:
    from dashboard_incidencias_app import dashboard_incidencias_app
except Exception:
    def dashboard_incidencias_app():
        st.subheader("📊 Dashboard incidencias")
        st.info("Módulo en construcción.")


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

    st.caption(
        f"{menu_logistica} / {submenu_logistica} / {opcion_logistica}"
    )

    st.divider()

    # =====================================================
    # EMBARQUES
    # =====================================================

    if opcion_logistica == "➕ Alta embarque":

        alta_embarque_app()

    elif opcion_logistica == "✏️ Actualizar estatus embarque":

        actualizar_estatus_embarque_app()

    elif opcion_logistica == "📋 Consulta embarque":

        consulta_embarques_app()

    elif opcion_logistica == "📊 Dashboard embarques":

        dashboard_embarques_app()

    elif opcion_logistica == "🛰️ Eventos embarque":

        eventos_embarque_app()

    elif opcion_logistica == "❌ Baja embarque":

        st.subheader("❌ Baja embarque")
        st.info("Módulo en construcción.")

    elif opcion_logistica == "✏️ Editar embarque":

        st.subheader("✏️ Editar embarque")
        st.info("Módulo en construcción.")

    # =====================================================
    # INCIDENCIAS
    # =====================================================

    elif opcion_logistica == "➕ Alta incidencia":

        alta_incidencia_app()

    elif opcion_logistica == "❌ Baja incidencia":

        baja_incidencia_app()

    elif opcion_logistica == "📋 Consulta incidencia":

        consulta_incidencia_app()

    elif opcion_logistica == "✏️ Actualizar incidencia":

        actualizar_incidencia_app()

    elif opcion_logistica == "✅ Cerrar incidencia":

        cerrar_incidencia_app()

    elif opcion_logistica == "📊 Dashboard incidencias":

        dashboard_incidencias_app()

    # =====================================================
    # DEFAULT
    # =====================================================

    else:

        st.subheader(opcion_logistica)

        st.info("Módulo de Logística en construcción.")

        st.write("Menú:", menu_logistica)
        st.write("Submenú:", submenu_logistica)
        st.write("Opción:", opcion_logistica)
