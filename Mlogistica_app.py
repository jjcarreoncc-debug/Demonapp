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


def limpiar_opcion(texto):
    return str(texto).strip().lower()


def inicio_logistica_app():

    st.markdown(
        """
        <style>
        .sigem-logistica-hero {
            position: relative;
            width: 100%;
            min-height: 520px;
            border-radius: 24px;
            overflow: hidden;
            background-image:
                linear-gradient(
                    rgba(10, 25, 45, 0.55),
                    rgba(10, 25, 45, 0.55)
                ),
                url("logologistica.jpg");
            background-size: cover;
            background-position: center;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 48px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        }

        .sigem-logistica-card {
            background: rgba(255, 255, 255, 0.88);
            border-radius: 24px;
            padding: 38px 44px;
            max-width: 780px;
            text-align: center;
            box-shadow: 0 12px 35px rgba(0,0,0,0.18);
        }

        .sigem-logistica-logo {
            font-size: 54px;
            margin-bottom: 8px;
        }

        .sigem-logistica-title {
            font-size: 40px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 8px;
        }

        .sigem-logistica-subtitle {
            font-size: 22px;
            color: #334155;
            margin-bottom: 22px;
        }

        .sigem-logistica-text {
            font-size: 17px;
            color: #475569;
            line-height: 1.7;
            margin-bottom: 24px;
        }

        .sigem-logistica-footer {
            font-size: 15px;
            color: #64748b;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        </style>

        <div class="sigem-logistica-hero">
            <div class="sigem-logistica-card">
                <div class="sigem-logistica-logo">🚚</div>

                <div class="sigem-logistica-title">
                    Bienvenido al módulo de Logística
                </div>

                <div class="sigem-logistica-subtitle">
                    SIGEM ERP
                </div>

                <div class="sigem-logistica-text">
                    Desde este módulo podrás administrar embarques,
                    transporte, rutas, seguimiento e incidencias logísticas.
                </div>

                <div class="sigem-logistica-footer">
                    TIDS · SIGEM · Gestión logística corporativa
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def logistica_app():

    if "opcion_logistica" not in st.session_state:
        st.session_state.opcion_logistica = "🏠 Inicio"

    menu_logistica, submenu_logistica, opcion_logistica = sidebar_logistica()

    if opcion_logistica is not None:
        st.session_state.opcion_logistica = opcion_logistica

    opcion_logistica = st.session_state.opcion_logistica
    opcion_limpia = limpiar_opcion(opcion_logistica)

    st.title("🚚 Logística")

    st.caption(
        f"{menu_logistica} / {submenu_logistica} / {opcion_logistica}"
    )

    st.divider()

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

        st.subheader("❌ Baja embarque")
        st.info("Módulo en construcción.")

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
