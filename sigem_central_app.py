import streamlit as st

from auth_app import login_app, logout_app
from Minventarios_app import inventarios_app
from sidebar_analitico import analitico_app
from mantenimiento_app import mantenimiento_app
from Mlogistica_app import logistica_app
from menu_dinamico import sidebar_dinamico


# =====================================================
# LOGIN
# =====================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "rol" not in st.session_state:
    st.session_state.rol = None

if not st.session_state.autenticado:
    login_app()
    st.stop()

logout_app()


# =====================================================
# SIDEBAR DINAMICO
# =====================================================

with st.sidebar:

    st.image(
        "logo1.png",
        width=100
    )

    st.markdown("## 🏢 SIGEM")
    st.caption("ERP Corporativo")

    st.markdown("---")

ruta = sidebar_dinamico()

with st.sidebar:

    st.markdown("---")

    st.caption(f"👤 {st.session_state.get('nombre', '')}")
    st.caption("SIGEM ERP")


# =====================================================
# ROUTER CENTRAL DINAMICO
# =====================================================

if ruta == "inventarios":

    inventarios_app()

elif ruta == "logistica":

    logistica_app()

elif ruta == "analitico":

    analitico_app()

elif ruta == "mantenimiento":

    mantenimiento_app()

else:

    st.info("Selecciona una opción del menú.")
