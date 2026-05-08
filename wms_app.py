
import streamlit as st
import pandas as pd
from wms_dashboard_app import wms_dashboard_app
from wms_indicadores_app import wms_indicadores_app
from wms_graficas_app import wms_graficas_app

from wms_carga_datos import cargar_datos_wms


# =========================
# CSS
# =========================
def aplicar_css_wms():

    st.markdown("""
    <style>

    div.stButton > button {
        width: 100%;
        height: 70px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        background-color: #16a085;
        color: white;
    }

    div.stButton > button:hover {
        background-color: #117864;
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)


# =========================
# APP WMS
# =========================
def wms_app():

    aplicar_css_wms()

    st.title("🏭 WMS")

    if "wms_vista" not in st.session_state:
        st.session_state.wms_vista = "menu"

    (
        inventario,
        ubicaciones,
        entradas,
        salidas,
        picking,
        packing,
        movimientos
    ) = cargar_datos_wms()

    carga_ok = all([
        inventario is not None,
        ubicaciones is not None,
        entradas is not None,
        salidas is not None,
        picking is not None,
        packing is not None,
        movimientos is not None
    ])

    if not carga_ok:

        st.warning(
            "⚠️ Error cargando archivos WMS."
        )

        return

    st.success(
        "✅ Datos WMS cargados correctamente."
    )

    # =========================
    # MENU
    # =========================
    if st.session_state.wms_vista == "menu":

        c1, c2 = st.columns(2)

        if c1.button("📊 Dashboard Ejecutivo"):
            st.session_state.wms_vista = "dashboard"
            st.rerun()

        if c2.button("📦 Operación"):
            st.session_state.wms_vista = "operacion"
            st.rerun()

        c3, c4 = st.columns(2)

        if c3.button("⚠️ Riesgos"):
            st.session_state.wms_vista = "riesgos"
            st.rerun()

        if c4.button("📈 Analítica"):
            st.session_state.wms_vista = "analitica"
            st.rerun()

    # =========================
    # BOTON VOLVER
    # =========================
    if st.session_state.wms_vista != "menu":

        if st.button("🔙 Volver"):

            st.session_state.wms_vista = "menu"

            st.rerun()

    # =========================
    # DASHBOARD
    # =========================
    if st.session_state.wms_vista == "dashboard":

        tab1, tab2, tab3 = st.tabs([
            "📊 Dashboard",
            "📌 Indicadores",
            "📈 Gráficas"
        ])

    with tab1:

        wms_dashboard_app(
            inventario,
            ubicaciones,
            entradas,
            salidas,
            picking,
            packing,
            movimientos
        )

    with tab2:

        wms_indicadores_app(
            inventario,
            ubicaciones,
            entradas,
            salidas,
            picking,
            packing,
            movimientos
        )

    with tab3:

        wms_graficas_app(
            inventario,
            ubicaciones,
            entradas,
            salidas,
            picking,
            packing,
            movimientos
        )
    # =========================
    # OPERACION
    # =========================
    elif st.session_state.wms_vista == "operacion":

        st.subheader("📦 Operación WMS")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Inventario",
            "Ubicaciones",
            "Entradas",
            "Salidas",
            "Picking",
            "Packing"
        ])

        with tab1:
            st.dataframe(
                inventario,
                use_container_width=True
            )

        with tab2:
            st.dataframe(
                ubicaciones,
                use_container_width=True
            )

        with tab3:
            st.dataframe(
                entradas,
                use_container_width=True
            )

        with tab4:
            st.dataframe(
                salidas,
                use_container_width=True
            )

        with tab5:
            st.dataframe(
                picking,
                use_container_width=True
            )

        with tab6:
            st.dataframe(
                packing,
                use_container_width=True
            )

    # =========================
    # RIESGOS
    # =========================
    elif st.session_state.wms_vista == "riesgos":

        st.subheader("⚠️ Riesgos WMS")

        if "ESTADO_STOCK" in inventario.columns:

            criticos = inventario[
                inventario["ESTADO_STOCK"] == "CRITICO"
            ]

            st.metric(
                "⚠️ Stock Crítico",
                len(criticos)
            )

            st.dataframe(
                criticos,
                use_container_width=True
            )

    # =========================
    # ANALITICA
    # =========================
    elif st.session_state.wms_vista == "analitica":

        st.subheader("📈 Analítica WMS")

        if "TIPO_MOVIMIENTO" in movimientos.columns:

            resumen = (
                movimientos
                .groupby("TIPO_MOVIMIENTO")
                .size()
                .reset_index(name="Cantidad")
            )

            st.bar_chart(
                resumen.set_index("TIPO_MOVIMIENTO")
            )

            st.dataframe(
                resumen,
                use_container_width=True
            )
