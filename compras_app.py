import streamlit as st
import pandas as pd

from compras_general_app import (
    dashboard_compras_general,
    top_compras_app,
    costos_compras_app,
    compras_sin_precio_app,
    detalle_compras_app
)


# =========================
# CSS COMPRAS
# =========================
def aplicar_css_compras():
    st.markdown("""
    <style>
        div.stButton > button {
            width: 100%;
            height: 70px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 12px;
            border: none;
            background-color: #1f77b4;
            color: white;
        }

        div.stButton > button:hover {
            background-color: #145a86;
            color: white;
        }

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


# =========================
# DASHBOARD COMPRAS
# =========================
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


# =========================
# APP COMPRAS
# =========================
def compras_app():

    aplicar_css_compras()

    st.title("🛒 Compras")

    # =========================
    # SESSION STATE
    # =========================
    if "compras_vista" not in st.session_state:
        st.session_state.compras_vista = "menu"

    # =========================
    # FILE UPLOADERS
    # =========================
    archivo_compras = st.file_uploader(
        "🛒 Compras",
        type=["xlsx"],
        key="compras_file"
    )

    archivo_productos = st.file_uploader(
        "📦 Productos",
        type=["xlsx"],
        key="productos_compras_file"
    )

    archivo_proveedores = st.file_uploader(
        "🏢 Proveedores",
        type=["xlsx"],
        key="proveedores_file"
    )

    archivo_bodegas = st.file_uploader(
        "🏬 Bodegas",
        type=["xlsx"],
        key="bodegas_file"
    )

    archivo_segmentacion = st.file_uploader(
        "🧩 Segmentación",
        type=["xlsx"],
        key="segmentacion_file"
    )

    # =========================
    # CARGA ARCHIVOS
    # =========================
    if archivo_compras:

        compras_df = pd.read_excel(archivo_compras)

        compras_df.rename(columns={
            "CANTIDAD": "ENTRADA"
        }, inplace=True)

        st.session_state.df_compras_base = compras_df

    if archivo_productos:
        st.session_state.df_productos_compras = pd.read_excel(archivo_productos)

    if archivo_proveedores:
        st.session_state.df_proveedores = pd.read_excel(archivo_proveedores)

    if archivo_bodegas:
        st.session_state.df_bodegas = pd.read_excel(archivo_bodegas)

    if archivo_segmentacion:
        st.session_state.df_segmentacion = pd.read_excel(archivo_segmentacion)

    # =========================
    # SESSION DATA
    # =========================
    compras = st.session_state.get("df_compras_base")
    productos = st.session_state.get("df_productos_compras")
    proveedores = st.session_state.get("df_proveedores")
    bodegas = st.session_state.get("df_bodegas")
    segmentacion = st.session_state.get("df_segmentacion")

    if (
        compras is None
        or productos is None
        or proveedores is None
        or bodegas is None
        or segmentacion is None
    ):
        st.warning("⚠️ Carga todos los archivos Excel de Compras")
        return

    # =========================
    # MERGES
    # =========================
    df = compras.merge(
        productos,
        on="NUMERO_PRODUCTO",
        how="left"
    )

    df = df.merge(
        proveedores,
        on="ID_PROVEEDOR",
        how="left"
    )

    df = df.merge(
        bodegas,
        on="ID_BODEGA",
        how="left"
    )

    df = df.merge(
        segmentacion,
        on="NUMERO_PRODUCTO",
        how="left"
    )

    # =========================
    # MENÚ
    # =========================
    if st.session_state.compras_vista == "menu":

        c1, c2, c3 = st.columns(3)

        if c1.button("📊 Dashboard"):
            st.session_state.compras_vista = "dashboard"
            st.rerun()

        if c2.button("📦 Productos"):
            st.session_state.compras_vista = "productos"
            st.rerun()

        if c3.button("🏢 Proveedores"):
            st.session_state.compras_vista = "proveedores"
            st.rerun()

        c4, c5, c6 = st.columns(3)

        if c4.button("🏬 Bodegas"):
            st.session_state.compras_vista = "bodegas"
            st.rerun()

        if c5.button("💰 Costos"):
            st.session_state.compras_vista = "costos"
            st.rerun()

        if c6.button("📋 Detalle"):
            st.session_state.compras_vista = "detalle"
            st.rerun()

    # =========================
    # BOTÓN VOLVER
    # =========================
    if st.session_state.compras_vista != "menu":

        if st.button("🔙 Volver"):
            st.session_state.compras_vista = "menu"
            st.rerun()

    # =========================
    # VISTAS
    # =========================
    if st.session_state.compras_vista == "dashboard":
        dashboard_compras(df)

    elif st.session_state.compras_vista == "productos":
        st.subheader("📦 Productos Comprados")
        st.dataframe(df, use_container_width=True)

    elif st.session_state.compras_vista == "proveedores":
        st.subheader("🏢 Proveedores")
        st.dataframe(df, use_container_width=True)

    elif st.session_state.compras_vista == "bodegas":
        st.subheader("🏬 Bodegas")
        st.dataframe(df, use_container_width=True)

    elif st.session_state.compras_vista == "costos":
        st.subheader("💰 Costos y Márgenes")
        st.dataframe(df, use_container_width=True)

    elif st.session_state.compras_vista == "detalle":
        st.subheader("📋 Detalle Compras")
        st.dataframe(df, use_container_width=True)
