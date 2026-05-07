import streamlit as st
import pandas as pd


def compras_app():

    st.title("🛒 Compras")

    # =========================
    # CARGA ARCHIVOS
    # =========================
    archivo_compras = st.file_uploader(
        "🛒 Compras",
        type=["xlsx"],
        key="compras"
    )

    archivo_productos = st.file_uploader(
        "📦 Productos",
        type=["xlsx"],
        key="productos_compras"
    )

    archivo_proveedores = st.file_uploader(
        "🏢 Proveedores",
        type=["xlsx"],
        key="proveedores"
    )

    archivo_bodegas = st.file_uploader(
        "🏬 Bodegas",
        type=["xlsx"],
        key="bodegas"
    )

    archivo_segmentacion = st.file_uploader(
        "🧩 Segmentación",
        type=["xlsx"],
        key="segmentacion"
    )

    # =========================
    # SESSION STATE
    # =========================
    if archivo_compras:
        st.session_state.df_compras_base = pd.read_excel(
            archivo_compras
        )

    if archivo_productos:
        st.session_state.df_productos_compras = pd.read_excel(
            archivo_productos
        )

    if archivo_proveedores:
        st.session_state.df_proveedores = pd.read_excel(
            archivo_proveedores
        )

    if archivo_bodegas:
        st.session_state.df_bodegas = pd.read_excel(
            archivo_bodegas
        )

    if archivo_segmentacion:
        st.session_state.df_segmentacion = pd.read_excel(
            archivo_segmentacion
        )

    # =========================
    # OBTENER DATAFRAMES
    # =========================
    compras = st.session_state.get(
        "df_compras_base"
    )

    productos = st.session_state.get(
        "df_productos_compras"
    )

    proveedores = st.session_state.get(
        "df_proveedores"
    )

    bodegas = st.session_state.get(
        "df_bodegas"
    )

    segmentacion = st.session_state.get(
        "df_segmentacion"
    )

    # =========================
    # VALIDACIÓN
    # =========================
    if (
        compras is None
        or productos is None
        or proveedores is None
        or bodegas is None
        or segmentacion is None
    ):

        st.warning(
            "⚠️ Carga todos los archivos Excel"
        )

        return

    # =========================
    # RELACIONES
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
    # SESSION MENU
    # =========================
    if "compras_vista" not in st.session_state:
        st.session_state.compras_vista = "menu"

    # =========================
    # MENÚ
    # =========================
    if st.session_state.compras_vista == "menu":

        c1, c2, c3 = st.columns(3)

        if c1.button("Dashboard"):
            st.session_state.compras_vista = "dashboard"
            st.rerun()

        if c2.button("Productos"):
            st.session_state.compras_vista = "productos"
            st.rerun()

        if c3.button("Proveedores"):
            st.session_state.compras_vista = "proveedores"
            st.rerun()

        c4, c5, c6 = st.columns(3)

        if c4.button("Bodegas"):
            st.session_state.compras_vista = "bodegas"
            st.rerun()

        if c5.button("Costos"):
            st.session_state.compras_vista = "costos"
            st.rerun()

        if c6.button("Detalle"):
            st.session_state.compras_vista = "detalle"
            st.rerun()

    # =========================
    # VOLVER
    # =========================
    if st.session_state.compras_vista != "menu":

        if st.button("🔙 Volver"):

            st.session_state.compras_vista = "menu"

            st.rerun()

    # =========================
    # VISTAS
    # =========================
    if st.session_state.compras_vista == "dashboard":

        st.subheader("📊 Dashboard Compras")

        st.dataframe(df.head())

    elif st.session_state.compras_vista == "productos":

        st.subheader("📦 Productos Comprados")

        st.dataframe(df)

    elif st.session_state.compras_vista == "proveedores":

        st.subheader("🏢 Proveedores")

        st.dataframe(df)

    elif st.session_state.compras_vista == "bodegas":

        st.subheader("🏬 Bodegas")

        st.dataframe(df)

    elif st.session_state.compras_vista == "costos":

        st.subheader("💰 Costos y Márgenes")

        st.dataframe(df)

    elif st.session_state.compras_vista == "detalle":

        st.subheader("📋 Detalle Compras")

        st.dataframe(df)
