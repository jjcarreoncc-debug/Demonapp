import streamlit as st

from Minventarios_app import inventarios_app
from sidebar_analitico import analitico_app
from mantenimiento_app import mantenimiento_app
from Mlogistica_app import logistica_app


def simular_login():

    st.session_state.autenticado = True
    st.session_state.usuario = "JCERVANTES"
    st.session_state.nombre = "JOSE JUANCERVANTES"
    st.session_state.rol = 1
    st.session_state.perfil = "ALL"


simular_login()


if "modulo_central" not in st.session_state:
    st.session_state.modulo_central = "📦 Minventarios"


with st.sidebar:

    # =========================
    # LOGO SIGEM
    # =========================
    st.image(
        "logo1.png",
        width=100
    )

    st.markdown("## 🏢 SIGEM")
    st.caption("ERP Corporativo")

    st.markdown("---")

    # =========================
    # MENU CENTRAL
    # =========================
    st.session_state.modulo_central = st.radio(
        "Módulos",
        [
            "📦 Minventarios",
            "📦 Mlogistica",
            "📊 Analíticos",
            "🛠️ Mantenimiento"
        ],
        key="menu_central_sigem"
    )

    st.markdown("---")

    st.caption(f"👤 {st.session_state.nombre}")
    st.caption("SIGEM ERP")


# =========================
# ROUTER CENTRAL
# =========================
if st.session_state.modulo_central == "📦 Minventarios":

    inventarios_app()

if st.session_state.modulo_central == "📦 Mlogistica":

    logistica_app()

elif st.session_state.modulo_central == "📊 Analíticos":

    analitico_app()

elif st.session_state.modulo_central == "🛠️ Mantenimiento":

    mantenimiento_app()
