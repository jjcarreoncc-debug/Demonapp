
import streamlit as st
import pandas as pd

from wms_dashboard_app import wms_dashboard_app
from wms_indicadores_app import wms_indicadores_app
from wms_graficas_app import wms_graficas_app

from wms_carga_datos import cargar_datos_wms


def aplicar_css_wms():

    st.markdown("""
    <style>
    section[data-testid="stFileUploader"] {
        background-color: #f5f7fa;
        padding: 16px;
        border-radius: 14px;
        border-left: 6px solid #16a085;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 18px;
    }
    </style>
    """, unsafe_allow_html=True)


def wms_app():

    aplicar_css_wms()

    st.title("🏭 WMS")

    vista = st.session_state.get(
        "menu_wms",
        "📊 Dashboard Ejecutivo"
    )

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
        st.warning("⚠️ Error cargando archivos WMS.")
        return
