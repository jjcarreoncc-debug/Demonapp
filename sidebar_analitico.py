
import streamlit as st

from compras_app import compras_app
from logistica_app import logistica_app
from inventarios_app import inventarios_app
from wms_app import wms_app


# =====================================
# LOGIN TEMPORAL
# =====================================
def simular_login():

    st.session_state.autenticado = True

    st.session_state.usuario = "JCERVANTES"

    st.session_state.nombre = "JOSE JUANCERVANTES"

    st.session_state.rol = 1

    st.session_state.perfil = "ALL"


simular_login()


# =====================================
# SIDEBAR ANALÍTICO
# =====================================
with st.sidebar:

    st.markdown("# 🏢 SIGEM")

    st.caption("Módulo Analítico")

    st.markdown("---")

    modulo = st.radio(
        "Área Operativa",
        [
            "🛒 Compras",
            "🚚 Logística",
            "🏬 WMS",
            "📦 Inventarios"
        ],
        key="sidebar_analitico_modulo"
    )

    st.markdown("---")

    st.caption(
        f"👤 {st.session_state.nombre}"
    )

    st.caption("SIGEM ERP")


# =====================================
# NAVEGACIÓN MÓDULOS
# =====================================
if modulo == "🛒 Compras":

    compras_app()

elif modulo == "🚚 Logística":

    logistica_app()

elif modulo == "🏬 WMS":

    wms_app()

elif modulo == "📦 Inventarios":

    inventarios_app()
