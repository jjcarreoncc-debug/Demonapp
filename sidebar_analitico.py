
import streamlit as st

from compras_app import compras_app
from inventarios_app import inventarios_app
from logistica_app import logistica_app
from wms_app import wms_app


def simular_login():

    st.session_state.autenticado = True
    st.session_state.usuario = "JCERVANTES"
    st.session_state.nombre = "JOSE JUANCERVANTES"
    st.session_state.rol = 1
    st.session_state.perfil = "ALL"


def analitico_app():

    simular_login()

    if "modulo_analitico" not in st.session_state:
        st.session_state.modulo_analitico = "compras"

    if "menu_compras" not in st.session_state:
        st.session_state.menu_compras = "📊 Dashboard"

    if "menu_logistica" not in st.session_state:
        st.session_state.menu_logistica = "📊 Dashboard Ejecutivo"

    if "menu_wms" not in st.session_state:
        st.session_state.menu_wms = "📊 Dashboard Ejecutivo"

    with st.sidebar:

        st.markdown("## 🏢 SIGEM")
        st.markdown("### 📊 Analítico")
        st.markdown("---")

        # =========================
        # COMPRAS
        # =========================
        with st.expander("🛒 Compras", expanded=True):

            if st.button(
                "📊 Dashboard",
                use_container_width=True,
                key="btn_compras_dashboard"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "📊 Dashboard"

            if st.button(
                "📦 Productos",
                use_container_width=True,
                key="btn_compras_productos"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "📦 Productos"

            if st.button(
                "🏢 Proveedores",
                use_container_width=True,
                key="btn_compras_proveedores"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "🏢 Proveedores"

            if st.button(
                "📈 Analítica",
                use_container_width=True,
                key="btn_compras_analitica"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "📈 Analítica"

            if st.button(
                "🏬 Bodegas",
                use_container_width=True,
                key="btn_compras_bodegas"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "🏬 Bodegas"

            if st.button(
                "💰 Costos",
                use_container_width=True,
                key="btn_compras_costos"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "💰 Costos"

            if st.button(
                "📋 Detalle",
                use_container_width=True,
                key="btn_compras_detalle"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "📋 Detalle"

        # =========================
        # LOGISTICA
        # =========================
        with st.expander("🚚 Logística", expanded=False):

            if st.button(
                "📊 Dashboard Ejecutivo",
                use_container_width=True,
                key="btn_logistica_dashboard"
            ):
                st.session_state.modulo_analitico = "logistica"
                st.session_state.menu_logistica = "📊 Dashboard Ejecutivo"

            if st.button(
                "📦 Operación",
                use_container_width=True,
                key="btn_logistica_operacion"
            ):
                st.session_state.modulo_analitico = "logistica"
                st.session_state.menu_logistica = "📦 Operación"

            if st.button(
                "⚠️ Riesgos",
                use_container_width=True,
                key="btn_logistica_riesgos"
            ):
                st.session_state.modulo_analitico = "logistica"
                st.session_state.menu_logistica = "⚠️ Riesgos"

            if st.button(
                "📈 Analítica",
                use_container_width=True,
                key="btn_logistica_analitica"
            ):
                st.session_state.modulo_analitico = "logistica"
                st.session_state.menu_logistica = "📈 Analítica"

        # =========================
        # INVENTARIOS
        # =========================
        with st.expander("📦 Inventarios", expanded=False):

            if st.button(
                "📦 Abrir Inventarios",
                use_container_width=True,
                key="btn_inventarios_abrir"
            ):
                st.session_state.modulo_analitico = "inventarios"

        # =========================
        # WMS
        # =========================
        with st.expander("🏬 WMS", expanded=False):

            if st.button(
                "📊 Dashboard Ejecutivo",
                use_container_width=True,
                key="btn_wms_dashboard"
            ):
                st.session_state.modulo_analitico = "wms"
                st.session_state.menu_wms = "📊 Dashboard Ejecutivo"

            if st.button(
                "📦 Operación",
                use_container_width=True,
                key="btn_wms_operacion"
            ):
                st.session_state.modulo_analitico = "wms"
                st.session_state.menu_wms = "📦 Operación"

            if st.button(
                "⚠️ Riesgos",
                use_container_width=True,
                key="btn_wms_riesgos"
            ):
                st.session_state.modulo_analitico = "wms"
                st.session_state.menu_wms = "⚠️ Riesgos"

            if st.button(
                "📈 Analítica",
                use_container_width=True,
                key="btn_wms_analitica"
            ):
                st.session_state.modulo_analitico = "wms"
                st.session_state.menu_wms = "📈 Analítica"

        st.markdown("---")
        st.caption(f"👤 {st.session_state.nombre}")
        st.caption("SIGEM ERP")

    # =========================
    # NAVEGACION
    # =========================
    if st.session_state.modulo_analitico == "compras":
        compras_app()

    elif st.session_state.modulo_analitico == "logistica":
        logistica_app()

    elif st.session_state.modulo_analitico == "inventarios":
        inventarios_app()

    elif st.session_state.modulo_analitico == "wms":
        wms_app()
