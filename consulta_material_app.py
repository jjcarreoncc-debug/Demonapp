import streamlit as st
import pandas as pd
import sqlite3


DB_NAME = "materiales.db"


def obtener_materiales():

    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT *
        FROM materiales
        ORDER BY codigo_material
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def consulta_materiales_app():

    st.title("🔍 Consulta de materiales")

    # =====================================================
    # CARGAR DATOS
    # =====================================================

    try:

        df = obtener_materiales()

    except Exception as e:

        st.error("❌ Error consultando materiales")
        st.exception(e)
        return

    # =====================================================
    # VALIDAR REGISTROS
    # =====================================================

    if df.empty:
        st.warning("No hay materiales registrados")
        return

    st.success(f"✅ Registros encontrados: {len(df)}")

    # =====================================================
    # RENOMBRAR COLUMNAS
    # =====================================================

    columnas = {
        "codigo_material": "Código",
        "descripcion": "Descripción",
        "categoria": "Categoría",
        "familia": "Familia",
        "unidad_base": "Unidad",
        "estatus": "Estatus",
        "stock_minimo": "Stock mínimo",
        "stock_maximo": "Stock máximo",
        "rotacion_abc": "ABC"
    }

    df = df.rename(columns=columnas)

    # =====================================================
    # FILTROS
    # =====================================================

    st.markdown("---")
    st.subheader("🎯 Filtros")

    c1, c2, c3 = st.columns(3)

    with c1:

        filtro_codigo = st.text_input("Código")

        categorias = (
            ["Todas"] +
            sorted(df["Categoría"].dropna().astype(str).unique())
        )

        filtro_categoria = st.selectbox(
            "Categoría",
            categorias
        )

    with c2:

        filtro_descripcion = st.text_input("Descripción")
        filtro_familia = st.text_input("Familia")

    with c3:

        estatus = (
            ["Todos"] +
            sorted(df["Estatus"].dropna().astype(str).unique())
        )

        filtro_estatus = st.selectbox(
            "Estatus",
            estatus
        )

        unidades = (
            ["Todas"] +
            sorted(df["Unidad"].dropna().astype(str).unique())
        )

        filtro_unidad = st.selectbox(
            "Unidad",
            unidades
        )

    # =====================================================
    # APLICAR FILTROS
    # =====================================================

    df_filtrado = df.copy()

    if filtro_codigo:

        df_filtrado = df_filtrado[
            df_filtrado["Código"].astype(str).str.contains(
                filtro_codigo,
                case=False,
                na=False
            )
        ]

    if filtro_descripcion:

        df_filtrado = df_filtrado[
            df_filtrado["Descripción"].astype(str).str.contains(
                filtro_descripcion,
                case=False,
                na=False
            )
        ]

    if filtro_categoria != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["Categoría"] == filtro_categoria
        ]

    if filtro_familia:

        df_filtrado = df_filtrado[
            df_filtrado["Familia"].astype(str).str.contains(
                filtro_familia,
                case=False,
                na=False
            )
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["Estatus"] == filtro_estatus
        ]

    if filtro_unidad != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["Unidad"] == filtro_unidad
        ]

    # =====================================================
    # RESULTADOS
    # =====================================================

    st.markdown("---")
    st.subheader("📋 Resultados")

    if df_filtrado.empty:
        st.warning("No se encontraron materiales")
        return

    columnas_tabla = [
        "Código",
        "Descripción",
        "Categoría",
        "Familia",
        "Unidad",
        "Estatus",
        "Stock mínimo",
        "Stock máximo",
        "ABC"
    ]

    columnas_existentes = [
        c for c in columnas_tabla
        if c in df_filtrado.columns
    ]

    st.dataframe(
        df_filtrado[columnas_existentes],
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # DETALLE
    # =====================================================

    st.markdown("---")
    st.subheader("📄 Detalle material")

    material = st.selectbox(
        "Selecciona material",
        df_filtrado["Código"].astype(str).tolist()
    )

    fila = df_filtrado[
        df_filtrado["Código"].astype(str) == material
    ].iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Código", fila.get("Código", ""))
        st.metric("Categoría", fila.get("Categoría", ""))

    with c2:
        st.metric("Unidad", fila.get("Unidad", ""))
        st.metric("Estatus", fila.get("Estatus", ""))

    with c3:
        st.metric("ABC", fila.get("ABC", ""))
        st.metric("Stock máximo", fila.get("Stock máximo", 0))

    st.info(f"Descripción: {fila.get('Descripción', '')}")

    # =====================================================
    # LOGÍSTICA
    # =====================================================

    with st.expander("📦 Datos logísticos"):

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Peso", fila.get("peso", 0))
            st.metric("Volumen", fila.get("volumen", 0))

        with c2:
            st.metric("Largo", fila.get("largo", 0))
            st.metric("Ancho", fila.get("ancho", 0))

        with c3:
            st.metric("Alto", fila.get("alto", 0))
            st.metric(
                "Tipo almacenamiento",
                fila.get("tipo_almacenamiento", "")
            )

    # =====================================================
    # COMERCIAL
    # =====================================================

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

    # =====================================================
    # INVENTARIO
    # =====================================================

    with st.expander("📊 Inventario"):

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Stock mínimo",
                fila.get("Stock mínimo", 0)
            )

            st.metric(
                "Stock máximo",
                fila.get("Stock máximo", 0)
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
                fila.get("ABC", "")
            )

            st.metric(
                "Unidad base",
                fila.get("Unidad", "")
            )

    # =====================================================
    # INTEGRACIONES
    # =====================================================

    with st.expander("🔗 Integraciones"):

        c1, c2 = st.columns(2)

        with c1:

            st.text_input(
                "Código barras",
                value=str(fila.get("codigo_barras", "")),
                disabled=True
            )

            st.text_input(
                "SKU base",
                value=str(fila.get("sku_base", "")),
                disabled=True
            )

        with c2:

            st.text_input(
                "Código SAP",
                value=str(fila.get("codigo_sap", "")),
                disabled=True
            )

            st.text_input(
                "Proveedor principal",
                value=str(fila.get("proveedor_principal", "")),
                disabled=True
            )


if __name__ == "__main__":
    consulta_materiales_app()
