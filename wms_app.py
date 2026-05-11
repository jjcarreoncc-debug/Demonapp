
import streamlit as st

from wms_dashboard_app import wms_dashboard_app
from wms_indicadores_app import wms_indicadores_app
from wms_graficas_app import wms_graficas_app
from wms_carga_datos import cargar_datos_wms


def wms_app():

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

    st.success("✅ Datos WMS cargados correctamente.")

    st.markdown("---")
    st.caption(f"Ruta: WMS / {vista}")

    if vista == "📊 Dashboard Ejecutivo":

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

    elif vista == "📦 Operación":

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
            st.dataframe(inventario, use_container_width=True)

        with tab2:
            st.dataframe(ubicaciones, use_container_width=True)

        with tab3:
            st.dataframe(entradas, use_container_width=True)

        with tab4:
            st.dataframe(salidas, use_container_width=True)

        with tab5:
            st.dataframe(picking, use_container_width=True)

        with tab6:
            st.dataframe(packing, use_container_width=True)

    elif vista == "⚠️ Riesgos":

        st.subheader("⚠️ Riesgos WMS")

        if "ESTADO_STOCK" in inventario.columns:

            criticos = inventario[
                inventario["ESTADO_STOCK"]
                .astype(str)
                .str.upper()
                .str.strip() == "CRITICO"
            ]

            st.metric("⚠️ Stock Crítico", len(criticos))

            st.dataframe(
                criticos,
                use_container_width=True
            )

    elif vista == "📈 Analítica":

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
