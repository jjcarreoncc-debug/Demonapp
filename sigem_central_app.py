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

if "ruta_central" not in st.session_state:
    st.session_state.ruta_central = "inventarios"


# =====================================================
# SIDEBAR CENTRAL
# =====================================================

with st.sidebar:

    st.image(
        "logo1.png",
        width=100
    )

    st.markdown("## 🏢 SIGEM")
    st.caption("ERP Corporativo")

    st.markdown("---")

    # =================================================
    # MODULOS PADRE
    # =================================================

    modulos_dict = {
        "📦 Minventarios": "inventarios",
        "📦 Mlogistica": "logistica",
        "📊 Analíticos": "analitico",
        "🛠️ Mantenimiento": "mantenimiento"
    }

    # =================================================
    # OBTENER LABEL ACTUAL
    # =================================================

    label_actual = "📦 Minventarios"

    for label, ruta in modulos_dict.items():

        if ruta == st.session_state.ruta_central:

            label_actual = label
            break

    # =================================================
    # RADIO CENTRAL
    # =================================================

    modulo_sel = st.radio(
        "Módulos",
        list(modulos_dict.keys()),
        index=list(modulos_dict.keys()).index(label_actual),
        key="menu_central_sigem"
    )

    # =================================================
    # GUARDAR RUTA
    # =================================================

    st.session_state.ruta_central = modulos_dict[
        modulo_sel
    ]

    st.markdown("---")

    st.caption(
        f"👤 {st.session_state.get('nombre', '')}"
    )

    st.caption("SIGEM ERP")


# =====================================================
# ROUTER CENTRAL
# =====================================================

ruta_central = st.session_state.get(
    "ruta_central",
    ""
)

if ruta_central == "inventarios":

    inventarios_app()

elif ruta_central == "logistica":

    logistica_app()

elif ruta_central == "analitico":

    analitico_app()

elif ruta_central == "mantenimiento":

    mantenimiento_app()

else:

    st.info(
        "Selecciona un módulo del menú lateral para comenzar."
    )
