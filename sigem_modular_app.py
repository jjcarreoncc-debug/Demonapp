import streamlit as st

from inventarios_app import inventarios_app
from compras_app import compras_app
from logistica_app import logistica_app
from wms_app import wms_app
from mantenimiento_app import mantenimiento_app


def sigem_modular_app():

    st.set_page_config(
        page_title="SIGEM Modular",
        page_icon="🧩",
        layout="wide"
    )

    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.title("🧩 SIGEM Modular")
        st.caption("Centro de módulos")

        ruta = st.radio(
            "Seleccione módulo",
            [
                "🏠 Inicio",
                "📦 Inventarios",
                "🛒 Compras",
                "🚚 Logística",
                "🏬 WMS",
                "🛠️ Mantenimiento"
            ]
        )

    # =====================================================
    # INICIO
    # =====================================================

    if ruta == "🏠 Inicio":

        st.title("🧩 SIGEM Modular")

        st.markdown("---")

        c1, c2, c3 = st.columns(3)

        with c1:

            st.info("📦 Inventarios")
            st.caption(
                "Control de materiales, movimientos y stock."
            )

        with c2:

            st.info("🛒 Compras")
            st.caption(
                "Órdenes de compra y proveedores."
            )

        with c3:

            st.info("🚚 Logística")
            st.caption(
                "Transporte y distribución."
            )

        c1, c2 = st.columns(2)

        with c1:

            st.info("🏬 WMS")
            st.caption(
                "Gestión de almacenes."
            )

        with c2:

            st.info("🛠️ Mantenimiento")
            st.caption(
                "Usuarios, permisos y configuración."
            )

    # =====================================================
    # INVENTARIOS
    # =====================================================

    elif ruta == "📦 Inventarios":

        st.title("📦 Inventarios")

        inventarios_app()

    # =====================================================
    # COMPRAS
    # =====================================================

    elif ruta == "🛒 Compras":

        st.title("🛒 Compras")

        compras_app()

    # =====================================================
    # LOGÍSTICA
    # =====================================================

    elif ruta == "🚚 Logística":

        st.title("🚚 Logística")

        logistica_app()

    # =====================================================
    # WMS
    # =====================================================

    elif ruta == "🏬 WMS":

        st.title("🏬 WMS")

        wms_app()

    # =====================================================
    # MANTENIMIENTO
    # =====================================================

    elif ruta == "🛠️ Mantenimiento":

        mantenimiento_app()


if __name__ == "__main__":
    sigem_modular_app()
