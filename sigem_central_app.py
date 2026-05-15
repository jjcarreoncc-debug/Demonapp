import streamlit as st

from auth_app import login_app, logout_app
from Minventarios_app import inventarios_app
from sidebar_analitico import analitico_app
from mantenimiento_app import mantenimiento_app
from Mlogistica_app import logistica_app


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
# MODULO DEFAULT
# =====================================================

if "modulo_central" not in st.session_state:
    st.session_state.modulo_central = "📦 Minventarios"


# =====================================================
# SIDEBAR FIJO TEMPORAL
# =====================================================

with st.sidebar:

    st.image(
        "logo1.png",
        width=100
    )

    st.markdown("## 🏢 SIGEM")
    st.caption("ERP Corporativo")

    st.markdown("---")

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

    st.caption(f"👤 {st.session_state.get('nombre', '')}")
    st.caption("SIGEM ERP")


# =====================================================
# ROUTER CENTRAL FIJO
# =====================================================
# =====================================================
# ROUTER CENTRAL DINÁMICO POR RUTA
# =====================================================

ruta_central = st.session_state.get("ruta_central", "")

if ruta_central == "inventarios":

    inventarios_app()

elif ruta_central == "logistica":

    logistica_app()

elif ruta_central == "analitico":

    analitico_app()

elif ruta_central == "mantenimiento":

    mantenimiento_app()

else:

    st.info("Selecciona un módulo del menú lateral para comenzar.")




