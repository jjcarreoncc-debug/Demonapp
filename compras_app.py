import streamlit as st
import pandas as pd

from compras_carga_datos import cargar_datos_compras

from compras_general_app import (
    dashboard_compras_general,
    top_compras_app,
    costos_compras_app,
    compras_sin_precio_app,
    detalle_compras_app
)


def aplicar_css_compras():
    st.markdown("""
    <style>
        section[data-testid="stFileUploader"] {
            background-color: #f5f7fa;
            padding: 16px;
            border-radius: 14px;
            border-left: 6px solid #1f77b4;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 18px;
        }

        section[data-testid="stFileUploader"] button {
            background-color: #1f77b4 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: bold !important;
        }
    </style>
    """, unsafe_allow_html=True)


def dashboard_compras(df):

    st.title("📥 Compras")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Dashboard",
        "Top Compras",
        "Costos",
        "Sin Precio",
        "Detalle"
    ])

    with tab1:
        dashboard_compras_general(df)

    with tab2:
        top_compras_app(df)

    with tab3:
        costos_compras_app(df)

    with tab4:
        compras_sin_precio_app(df)

    with tab5:
        detalle_compras_app(df)


def compras_app():

    aplicar_css_compras()

    st.title("🛒 Compras")

    vista = st.session_state.get(
        "menu_compras",
        "📊 Dashboard"
    )

    (
        compras,
        productos,
        proveedores,
        bodegas,
        segmentacion
    ) = cargar_datos_compras()

    carga_automatica_ok = all([
        compras is not None,
        productos is not None,
        proveedores is not None,
        bodegas is not None,
        segmentacion is not None
    ])

    if carga_automatica_ok:
        st.success("✅ Datos de compras cargados automáticamente desde GitHub.")

        if "CANTIDAD" in compras.columns:
            compras = compras.rename(columns={"CANTIDAD": "ENTRADA"})

    else:
        st.warning("⚠️ No se pudieron cargar los archivos automáticos. Usa carga manual.")

        archivo_compras = st.file_uploader("🛒 Compras", type=["xlsx"], key="compras_file")
        archivo_productos = st.file_uploader("📦 Productos", type=["xlsx"], key="productos_compras_file")
        archivo_proveedores = st.file_uploader("🏢 Proveedores", type=["xlsx"], key="proveedores_file")
        archivo_bodegas = st.file_uploader("🏬 Bodegas", type=["xlsx"], key="bodegas_file")
        archivo_segmentacion = st.file_uploader("🧩 Segmentación", type=["xlsx"], key="segmentacion_file")

        if archivo_compras:
            compras = pd.read_excel(archivo_compras)

            if "CANTIDAD" in compras.columns:
                compras.rename(columns={"CANTIDAD": "ENTRADA"}, inplace=True)

        if archivo_productos:
            productos = pd.read_excel(archivo_productos)

        if archivo_proveedores:
            proveedores = pd.read_excel(archivo_proveedores)

        if archivo_bodegas:
            bodegas = pd.read_excel(archivo_bodegas)

        if archivo_segmentacion:
            segmentacion = pd.read_excel(archivo_segmentacion)

    if (
        compras is None
        or productos is None
        or proveedores is None
        or bodegas is None
        or segmentacion is None
    ):
        st.warning("⚠️ Carga todos los archivos Excel de Compras")
        return

    for df_tmp in [compras, productos, proveedores, bodegas, segmentacion]:
        df_tmp.columns = df_tmp.columns.astype(str).str.strip()

    for df_tmp in [compras, productos, segmentacion]:
        if "NUMERO_PRODUCTO" in df_tmp.columns:
            df_tmp["NUMERO_PRODUCTO"] = (
                df_tmp["NUMERO_PRODUCTO"]
                .astype(str)
                .str.strip()
            )

    for df_tmp in [compras, proveedores]:
        if "ID_PROVEEDOR" in df_tmp.columns:
            df_tmp["ID_PROVEEDOR"] = (
                df_tmp["ID_PROVEEDOR"]
                .astype(str)
                .str.strip()
            )

    for df_tmp in [compras, bodegas]:
        if "ID_BODEGA" in df_tmp.columns:
            df_tmp["ID_BODEGA"] = (
                df_tmp["ID_BODEGA"]
                .astype(str)
                .str.strip()
            )

    df = compras.copy()

    if "NUMERO_PRODUCTO" in df.columns and "NUMERO_PRODUCTO" in productos.columns:
        df = df.merge(productos, on="NUMERO_PRODUCTO", how="left")

    if "ID_PROVEEDOR" in df.columns and "ID_PROVEEDOR" in proveedores.columns:
        df = df.merge(proveedores, on="ID_PROVEEDOR", how="left")

    if "ID_BODEGA" in df.columns and "ID_BODEGA" in bodegas.columns:
        df = df.merge(bodegas, on="ID_BODEGA", how="left")

    if "NUMERO_PRODUCTO" in df.columns and "NUMERO_PRODUCTO" in segmentacion.columns:
        df = df.merge(segmentacion, on="NUMERO_PRODUCTO", how="left")

    st.markdown("---")
    st.caption(f"Ruta: Compras / {vista}")

    if vista == "📊 Dashboard":
        dashboard_compras(df)

    elif vista == "📦 Productos":
        st.subheader("📦 Productos Comprados")
        st.dataframe(df, use_container_width=True)

    elif vista == "🏢 Proveedores":
        st.subheader("🏢 Proveedores")
        st.dataframe(df, use_container_width=True)

    elif vista == "🏬 Bodegas":
        st.subheader("🏬 Bodegas")
        st.dataframe(df, use_container_width=True)

    elif vista == "💰 Costos":
        st.subheader("💰 Costos y Márgenes")
        st.dataframe(df, use_container_width=True)

    elif vista == "📋 Detalle":
        st.subheader("📋 Detalle Compras")
        st.dataframe(df, use_container_width=True)

    elif vista == "📈 Analítica":

        try:
            from compras_analitica_app import compras_analitica_app

            compras_analitica_app(df)

        except Exception as e:
            st.error("Error cargando Analítica de Compras.")
            st.exception(e)
