import streamlit as st
import pandas as pd

from materiales_db import consultar_materiales


def consulta_material_app():

    st.title("🔍 Consulta de material")

    st.caption(
        "Maestros / Productos / Maestro de materiales / Consulta de material"
    )

    data = consultar_materiales()

    if not data:
        st.warning("No hay materiales registrados.")
        return

    df = pd.DataFrame(data)

    st.subheader("📋 Materiales registrados")

    columnas = [
        "codigo_material",
        "descripcion",
        "categoria",
        "familia",
        "unidad_base",
        "estatus"
    ]

    columnas_existentes = [
        c for c in columnas
        if c in df.columns
    ]

    st.dataframe(
        df[columnas_existentes],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    material = st.selectbox(
        "Selecciona material",
        df["codigo_material"].tolist()
    )

    fila = df[
        df["codigo_material"] == material
    ].iloc[0]

    st.subheader("📄 Detalle material")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Código",
            fila.get("codigo_material", "")
        )

        st.metric(
            "Categoría",
            fila.get("categoria", "")
        )

    with c2:
        st.metric(
            "Unidad",
            fila.get("unidad_base", "")
        )

        st.metric(
            "Estatus",
            fila.get("estatus", "")
        )

    with c3:
        st.metric(
            "ABC",
            fila.get("rotacion_abc", "")
        )

        st.metric(
            "Stock máximo",
            fila.get("stock_maximo", 0)
        )

    st.info(
        f"Descripción: {fila.get('descripcion', '')}"
    )

    # =========================
    # DATOS LOGISTICOS
    # =========================
    with st.expander("📦 Datos logísticos", expanded=True):

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Peso",
                fila.get("peso", 0)
            )

            st.metric(
                "Volumen",
                fila.get("volumen", 0)
            )

        with c2:
            st.metric(
                "Largo",
                fila.get("largo", 0)
            )

            st.metric(
                "Ancho",
                fila.get("ancho", 0)
            )

        with c3:
            st.metric(
                "Alto",
                fila.get("alto", 0)
            )

            st.metric(
                "Tipo almacenamiento",
                fila.get("tipo_almacenamiento", "")
            )

    # =========================
    # DATOS COMERCIALES
    # =========================
    with st.expander("💲 Datos comerciales"):

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Costo estándar",
                fila.get("costo_estandar", 0)
            )

            st.metric(
                "Precio compra",
                fila.get("precio_compra", 0)
            )

        with c2:

            st.metric(
                "Precio venta",
                fila.get("precio_venta", 0)
            )

            st.metric(
                "Moneda",
                fila.get("moneda", "")
            )

        with c3:

            st.metric(
                "Impuesto",
                fila.get("impuesto", "")
            )

            st.metric(
                "Margen %",
                fila.get("margen_objetivo", 0)
            )

    # =========================
    # INVENTARIO
    # =========================
    with st.expander("📊 Inventario"):

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Stock mínimo",
                fila.get("stock_minimo", 0)
            )

            st.metric(
                "Stock máximo",
                fila.get("stock_maximo", 0)
            )

        with c2:

            st.metric(
                "Punto reorden",
                fila.get("punto_reorden", 0)
            )

            st.metric(
                "Lead time",
                fila.get("lead_time", 0)
            )

        with c3:

            st.metric(
                "ABC",
                fila.get("rotacion_abc", "")
            )

            st.metric(
                "Unidad base",
                fila.get("unidad_base", "")
            )

    # =========================
    # INTEGRACIONES
    # =========================
    with st.expander("🔗 Integraciones"):

        c1, c2 = st.columns(2)

        with c1:

            st.text_input(
                "Código barras",
                value=fila.get("codigo_barras", ""),
                disabled=True
            )

            st.text_input(
                "SKU base",
                value=fila.get("sku_base", ""),
                disabled=True
            )

        with c2:

            st.text_input(
                "Código SAP",
                value=fila.get("codigo_sap", ""),
                disabled=True
            )

            st.text_input(
                "Proveedor principal",
                value=fila.get("proveedor_principal", ""),
                disabled=True
            )
