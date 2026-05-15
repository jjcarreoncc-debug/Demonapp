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


# =========================
# MODULO DEFAULT
# =========================

if "modulo_central" not in st.session_state:

    st.session_state.modulo_central = "📦 Minventarios"


# =========================
# SIDEBAR
# =========================

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

elif st.session_state.modulo_central == "📦 Mlogistica":

    logistica_app()

elif st.session_state.modulo_central == "📊 Analíticos":

    analitico_app()

elif st.session_state.modulo_central == "🛠️ Mantenimiento":

    mantenimiento_app()
