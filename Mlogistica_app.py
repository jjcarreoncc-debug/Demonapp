import streamlit as st
import base64
from pathlib import Path

from sidebar_logistica import sidebar_logistica

from alta_embarque_app import alta_embarque_app
from consulta_embarques_app import consulta_embarques_app
from actualizar_estatus_embarque_app import actualizar_estatus_embarque_app
from dashboard_embarques_app import dashboard_embarques_app
from eventos_embarque_app import eventos_embarque_app

from alta_incidencia_app import alta_incidencia_app
from dashboard_incidencias_app import dashboard_incidencias_app


BASE_DIR = Path(__file__).resolve().parent


def get_base64_image(image_path):

    file_path = BASE_DIR / image_path

    if not file_path.exists():

        return None

    with open(file_path, "rb") as img_file:

        return base64.b64encode(
            img_file.read()
        ).decode()


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

    bg_image = get_base64_image(
        "logologistica.jpg"
    )

    sigem_logo = get_base64_image(
        "logo1.png"
    )

    tids_logo = get_base64_image(
        "LOOGO-TIDS-CONSULTING (2).jpg"
    )

    if bg_image:

        fondo_css = f"""
        background-image:
            linear-gradient(
                rgba(0,0,0,0.45),
                rgba(0,0,0,0.45)
            ),
            url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        """

    else:

        fondo_css = "background-color: #0f172a;"

    sigem_html = ""

    if sigem_logo:

        sigem_html = (
            f'<img src="data:image/png;base64,{sigem_logo}" width="170">'
        )

    else:

        sigem_html = (
            '<span style="color:white;font-size:28px;font-weight:800;">SIGEM</span>'
        )

    tids_html = ""

    if tids_logo:

        tids_html = (
            f'<img src="data:image/jpg;base64,{tids_logo}" width="170">'
        )

    else:

        tids_html = (
            '<span style="color:white;font-size:22px;font-weight:700;">TIDS Consulting</span>'
        )

    st.markdown(
        f"""
        <style>

        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }}

        .sigem-logistica-full {{
            min-height: 72vh;
            width: 100%;
            border-radius: 24px;
            overflow: hidden;
            {fondo_css}
            box-shadow: 0 20px 60px rgba(0,0,0,0.30);
            position: relative;
            padding: 32px 40px;
        }}

        .sigem-logistica-logos {{
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .sigem-logistica-center {{
            min-height: 52vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .sigem-logistica-card {{
            background: rgba(15, 23, 42, 0.68);
            border-radius: 30px;
            padding: 42px 58px;
            width: 760px;
            max-width: 92%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
            border: 1px solid rgba(255,255,255,0.14);
            backdrop-filter: blur(6px);
        }}

        .sigem-logistica-title {{
            font-size: 46px;
            font-weight: 800;
            color: white;
            margin-bottom: 8px;
            text-shadow: 0 5px 20px rgba(0,0,0,0.40);
        }}

        .sigem-logistica-subtitle {{
            font-size: 22px;
            color: white;
            margin-bottom: 26px;
            text-shadow: 0 5px 20px rgba(0,0,0,0.40);
        }}

        .sigem-logistica-text {{
            font-size: 18px;
            color: rgba(255,255,255,0.88);
            line-height: 1.8;
            margin-top: 20px;
        }}

        .sigem-logistica-footer {{
            margin-top: 30px;
            color: rgba(255,255,255,0.75);
            font-size: 14px;
            letter-spacing: 0.5px;
        }}

        </style>

        <div class="sigem-logistica-full">

            <div class="sigem-logistica-logos">
                <div>
                    {tids_html}
                </div>

                <div>
                    {sigem_html}
                </div>
            </div>

            <div class="sigem-logistica-center">

                <div class="sigem-logistica-card">

                    <div class="sigem-logistica-title">
                        🚚 Logística
                    </div>

                    <div class="sigem-logistica-subtitle">
                        Bienvenido al módulo de logística SIGEM
                    </div>

                    <div class="sigem-logistica-text">
                        Desde este módulo podrás administrar embarques,
                        transporte, rutas, seguimiento e incidencias logísticas.
                    </div>

                    <div class="sigem-logistica-footer">
                        TIDS · SIGEM ERP · Gestión logística corporativa
                    </div>

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

    opcion_limpia = limpiar_opcion(
        opcion_logistica
    )

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
