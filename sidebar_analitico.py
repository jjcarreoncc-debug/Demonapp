
import streamlit as st

from compras_app import compras_app
from inventarios_app import inventarios_app
from logistica_app import logistica_app
from dashboard_stock_app import dashboard_stock_app
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

    if "menu_inventarios" not in st.session_state:
        st.session_state.menu_inventarios = "📊 Dashboard General"

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
                st.rerun()

            if st.button(
                "📦 Productos",
                use_container_width=True,
                key="btn_compras_productos"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "📦 Productos"
                st.rerun()

            if st.button(
                "🏢 Proveedores",
                use_container_width=True,
                key="btn_compras_proveedores"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "🏢 Proveedores"
                st.rerun()

            if st.button(
                "📈 Analítica",
                use_container_width=True,
                key="btn_compras_analitica"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "📈 Analítica"
                st.rerun()

            if st.button(
                "🏬 Bodegas",
                use_container_width=True,
                key="btn_compras_bodegas"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "🏬 Bodegas"
                st.rerun()

            if st.button(
                "💰 Costos",
                use_container_width=True,
                key="btn_compras_costos"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "💰 Costos"
                st.rerun()

            if st.button(
                "📋 Detalle",
                use_container_width=True,
                key="btn_compras_detalle"
            ):
                st.session_state.modulo_analitico = "compras"
                st.session_state.menu_compras = "📋 Detalle"
                st.rerun()

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
                st.rerun()

            if st.button(
                "📦 Operación",
                use_container_width=True,
                key="btn_logistica_operacion"
            ):
                st.session_state.modulo_analitico = "logistica"
                st.session_state.menu_logistica = "📦 Operación"
                st.rerun()

            if st.button(
                "⚠️ Riesgos",
                use_container_width=True,
                key="btn_logistica_riesgos"
            ):
                st.session_state.modulo_analitico = "logistica"
                st.session_state.menu_logistica = "⚠️ Riesgos"
                st.rerun()

            if st.button(
                "📈 Analítica",
                use_container_width=True,
                key="btn_logistica_analitica"
            ):
                st.session_state.modulo_analitico = "logistica"
                st.session_state.menu_logistica = "📈 Analítica"
                st.rerun()

        # =========================
        # INVENTARIOS
        # =========================
        with st.expander("📦 Inventarios", expanded=False):

            if st.button(
                "📊 Dashboard General",
                use_container_width=True,
                key="btn_inv_dashboard"
            ):
                st.session_state.modulo_analitico = "inventarios"
                st.session_state.menu_inventarios = "📊 Dashboard General"
                st.rerun()

            if st.button(
                "🚨 Críticos",
                use_container_width=True,
                key="btn_inv_criticos"
            ):
                st.session_state.modulo_analitico = "inventarios"
                st.session_state.menu_inventarios = "🚨 Críticos"
                st.rerun()

            if st.button(
                "⚠️ Sobrestock",
                use_container_width=True,
                key="btn_inv_sobrestock"
            ):
                st.session_state.modulo_analitico = "inventarios"
                st.session_state.menu_inventarios = "⚠️ Sobrestock"
                st.rerun()

            if st.button(
                "🔄 Rotación",
                use_container_width=True,
                key="btn_inv_rotacion"
            ):
                st.session_state.modulo_analitico = "inventarios"
                st.session_state.menu_inventarios = "🔄 Rotación"
                st.rerun()
            
            if st.button(
                "🔎 Trazabilidad",
                use_container_width=True,
                key="btn_inv_trazabilidad"
            ):
                 st.session_state.modulo_analitico = "inventarios"
                 st.session_state.menu_inventarios = "🔎 Trazabilidad"
                 st.rerun()

            if st.button(
                "🤖 IA",
                use_container_width=True,
                key="btn_inv_ia"
            ):
                st.session_state.modulo_analitico = "inventarios"
                st.session_state.menu_inventarios = "🤖 IA"
                st.rerun()

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
                st.rerun()

            if st.button(
                "📦 Operación",
                use_container_width=True,
                key="btn_wms_operacion"
            ):
                st.session_state.modulo_analitico = "wms"
                st.session_state.menu_wms = "📦 Operación"
                st.rerun()

            if st.button(
                "⚠️ Riesgos",
                use_container_width=True,
                key="btn_wms_riesgos"
            ):
                st.session_state.modulo_analitico = "wms"
                st.session_state.menu_wms = "⚠️ Riesgos"
                st.rerun()

            if st.button(
                "📈 Analítica",
                use_container_width=True,
                key="btn_wms_analitica"
            ):
                st.session_state.modulo_analitico = "wms"
                st.session_state.menu_wms = "📈 Analítica"
                st.rerun()

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
        dashboard_stock_app()

    elif st.session_state.modulo_analitico == "wms":
        wms_app()
