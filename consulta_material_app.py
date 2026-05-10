import streamlit as st
import pandas as pd

from materiales_db import consultar_materiales


def consulta_material_app():

    st.title("🔍 Consulta de material")
    st.caption("Maestros / Productos / Maestro de materiales / Consulta de material")

    data = consultar_materiales()

    if not data:
        st.warning("No hay materiales registrados en la base de datos.")
        return

    df = pd.DataFrame(data)

    df = df.rename(columns={
        "codigo_material": "Código",
        "descripcion": "Descripción",
        "categoria": "Categoría",
        "familia": "Familia",
        "unidad_base": "Unidad",
        "estatus": "Estatus",
        "stock_minimo": "Stock mínimo",
        "stock_maximo": "Stock máximo",
        "rotacion_abc": "ABC"
    })

    st.subheader("🎯 Filtros de búsqueda")

    c1, c2, c3 = st.columns(3)

    with c1:
        filtro_codigo = st.text_input("Código material")
        filtro_categoria = st.selectbox(
            "Categoría",
            ["Todas"] + sorted(df["Categoría"].dropna().astype(str).unique().tolist())
        )

    with c2:
        filtro_descripcion = st.text_input("Descripción")
        filtro_familia = st.text_input("Familia")

    with c3:
        filtro_estatus = st.selectbox(
            "Estatus",
            ["Todos"] + sorted(df["Estatus"].dropna().astype(str).unique().tolist())
        )
        filtro_unidad = st.selectbox(
            "Unidad base",
            ["Todas"] + sorted(df["Unidad"].dropna().astype(str).unique().tolist())
        )

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
        df_filtrado = df_filtrado[df_filtrado["Categoría"] == filtro_categoria]

    if filtro_familia:
        df_filtrado = df_filtrado[
            df_filtrado["Familia"].astype(str).str.contains(
                filtro_familia,
                case=False,
                na=False
            )
        ]

    if filtro_estatus != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estatus"] == filtro_estatus]

    if filtro_unidad != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Unidad"] == filtro_unidad]

    st.markdown("---")
    st.subheader("📋 Resultados")

    columnas_mostrar = [
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
        c for c in columnas_mostrar
        if c in df_filtrado.columns
    ]

    if df_filtrado.empty:
        st.warning("No se encontraron materiales con esos filtros.")
        return

    st.dataframe(
        df_filtrado[columnas_existentes],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("📄 Detalle del material")

    material = st.selectbox(
        "Selecciona material",
        df_filtrado["Código"].astype(str).tolist()
    )

    fila = df_filtrado[df_filtrado["Código"].astype(str) == material].iloc[0]

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Código", fila.get("Código", ""))
        st.metric("Categoría", fila.get("Categoría", ""))

    with c2:
        st.metric("Unidad", fila.get("Unidad", ""))
        st.metric("Estatus", fila.get("Estatus", ""))

    with c3:
        st.metric("ABC", fila.get("ABC", ""))
        st.metric("Stock máx.", fila.get("Stock máximo", 0))

    st.info(f"Descripción: {fila.get('Descripción', '')}")

  
    
   # 
   
   #
    with st.expander("📦 Datos logísticos", expanded=True):

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
#
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
    
    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.button("✏️ Modificar material")

    with c2:
        st.button("❌ Solicitar baja")

    with c3:
        st.button("📥 Exportar consulta")
