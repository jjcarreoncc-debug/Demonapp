import streamlit as st

from sidebar_logistica import sidebar_logistica

from alta_embarque_app import alta_embarque_app
from consulta_embarques_app import consulta_embarques_app
from actualizar_estatus_embarque_app import actualizar_estatus_embarque_app
from dashboard_embarques_app import dashboard_embarques_app
from eventos_embarque_app import eventos_embarque_app

from alta_incidencia_app import alta_incidencia_app
from dashboard_incidencias_app import dashboard_incidencias_app



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


try:

    from baja_embarque_app import (
        baja_embarque_app
    )

except Exception as e:

    st.error(
        "Error cargando baja_embarque_app"
    )

    st.exception(e)


def limpiar_opcion(texto):

    return str(texto).strip().lower()


def inicio_logistica_app():

    st.title("🚚 Bienvenido al módulo de Logística")

    st.markdown(
        """
        <style>
    
        .block-container {
            padding-top: 2rem;
        }
    
        </style>
        """,
        unsafe_allow_html=True
    )
        

    st.image(
        "logologistica.jpg",
        use_container_width=True
    )

    
def logistica_app():

    if "opcion_logistica" not in st.session_state:

        st.session_state.opcion_logistica = "🏠 Inicio"

    menu_logistica, submenu_logistica, opcion_logistica = sidebar_logistica()

    if opcion_logistica is not None:

        st.session_state.opcion_logistica = opcion_logistica

    opcion_logistica = st.session_state.opcion_logistica

    opcion_limpia = limpiar_opcion(
        opcion_logistica
    )
    ##############################################3
           
    #################################333
    if opcion_limpia == limpiar_opcion("🏠 Inicio"):

        inicio_logistica_app()

    elif opcion_limpia == limpiar_opcion("➕ Alta embarque"):

        alta_embarque_app()

    elif opcion_limpia == limpiar_opcion("✏️ Actualizar estatus embarque"):

        actualizar_estatus_embarque_app()

    elif opcion_limpia == limpiar_opcion("📋 Consulta embarque"):

        consulta_embarques_app()

    elif opcion_limpia == limpiar_opcion("📊 Dashboard embarques"):

        dashboard_embarques_app()

    elif opcion_limpia == limpiar_opcion("🛰️ Eventos embarque"):

        eventos_embarque_app()

    elif opcion_limpia == limpiar_opcion("❌ Baja embarque"):

        baja_embarque_app()

    elif opcion_limpia == limpiar_opcion("✏️ Editar embarque"):

        st.subheader("✏️ Editar embarque")
        st.info("Módulo en construcción.")

    elif opcion_limpia == limpiar_opcion("➕ Alta incidencia"):

        alta_incidencia_app()

    elif opcion_limpia == limpiar_opcion("❌ Baja incidencia"):

        baja_incidencia_app()

    elif opcion_limpia == limpiar_opcion("📋 Consulta incidencia"):

        consulta_incidencia_app()

    elif opcion_limpia == limpiar_opcion("✏️ Actualizar incidencia"):

        actualizar_incidencia_app()

    elif opcion_limpia == limpiar_opcion("✅ Cerrar incidencia"):

        cerrar_incidencia_app()

    elif opcion_limpia == limpiar_opcion("📊 Dashboard incidencias"):

        dashboard_incidencias_app()

    else:

        st.subheader(opcion_logistica)
        st.info("Módulo de Logística en construcción.")

        st.write("Menú:", menu_logistica)
        st.write("Submenú:", submenu_logistica)
        st.write("Opción:", opcion_logistica)
        st.write("Opción limpia:", opcion_limpia)
