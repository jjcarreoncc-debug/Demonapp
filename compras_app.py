import streamlit as st
import pandas as pd
import plotly.express as px
from ui_components import card_kp

# =========================
# CSS COMPRAS
# =========================
def aplicar_css_compras():
    st.markdown("""
    <style>
        /* Botones de menú */
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

        /* Contenedor file_uploader */
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

    st.subheader("📊 Dashboard Compras")

    df = df.copy()

    df["COSTO_TOTAL"] = df["CANTIDAD"] * df["COSTO_UNITARIO"]
    df["VENTA_TOTAL_ESTIMADA"] = df["CANTIDAD"] * df["PRECIO_VENTA"]
    df["MARGEN_TOTAL"] = df["VENTA_TOTAL_ESTIMADA"] - df["COSTO_TOTAL"]

    total_comprado = int(df["CANTIDAD"].sum())
    costo_total = df["COSTO_TOTAL"].sum()
    margen_total = df["MARGEN_TOTAL"].sum()
    productos_comprados = df["NUMERO_PRODUCTO"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        card_kpi("🛒 Unidades Compradas", f"{total_comprado:,}", "#3498db")

    with c2:
        card_kpi("💰 Costo Total", f"${costo_total:,.0f}", "#e67e22")

    with c3:
        card_kpi("📈 Margen Estimado", f"${margen_total:,.0f}", "#2ecc71")

    with c4:
        card_kpi("📦 Productos", productos_comprados, "#8e44ad")

    st.divider()

    st.markdown("### 🔥 Top productos comprados")

    top = (
        df.groupby("NOMBRE_PRODUCTO")["CANTIDAD"]
        .sum()
        .reset_index()
        .sort_values("CANTIDAD", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top,
        x="CANTIDAD",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="CANTIDAD",
        title="Top 10 productos comprados"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Vista rápida")
    st.dataframe(df.head(20), use_container_width=True)
# =========================
# APP COMPRAS
# =========================
def compras_app():

    aplicar_css_compras()

    st.title("🛒 Compras")

    if "compras_vista" not in st.session_state:
        st.session_state.compras_vista = "menu"

    # =========================
    # CARGA ARCHIVOS
    # =========================
    archivo_compras = st.file_uploader("🛒 Compras", type=["xlsx"], key="compras_file")
    archivo_productos = st.file_uploader("📦 Productos", type=["xlsx"], key="productos_compras_file")
    archivo_proveedores = st.file_uploader("🏢 Proveedores", type=["xlsx"], key="proveedores_file")
    archivo_bodegas = st.file_uploader("🏬 Bodegas", type=["xlsx"], key="bodegas_file")
    archivo_segmentacion = st.file_uploader("🧩 Segmentación", type=["xlsx"], key="segmentacion_file")

    if archivo_compras:
        st.session_state.df_compras_base = pd.read_excel(archivo_compras)
    if archivo_productos:
        st.session_state.df_productos_compras = pd.read_excel(archivo_productos)
    if archivo_proveedores:
        st.session_state.df_proveedores = pd.read_excel(archivo_proveedores)
    if archivo_bodegas:
        st.session_state.df_bodegas = pd.read_excel(archivo_bodegas)
    if archivo_segmentacion:
        st.session_state.df_segmentacion = pd.read_excel(archivo_segmentacion)

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
    # RELACIONES
    # =========================
    df = compras.merge(productos, on="NUMERO_PRODUCTO", how="left")
    df = df.merge(proveedores, on="ID_PROVEEDOR", how="left")
    df = df.merge(bodegas, on="ID_BODEGA", how="left")
    df = df.merge(segmentacion, on="NUMERO_PRODUCTO", how="left")

    # =========================
    # MENÚ COMPRAS
    # =========================
    if st.session_state.compras_vista == "menu":
        # Primera fila: 3 botones
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

        # Segunda fila: 3 botones (c6 vacío)
        c4, c5, c6 = st.columns([1,1,1])
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
    # VOLVER
    # =========================
    if st.session_state.compras_vista != "menu":
        if st.button("🔙 Volver"):
            st.session_state.compras_vista = "menu"
            st.rerun()

    # =========================
    # VISTAS TEMPORALES
    # =========================
    if st.session_state.compras_vista == "dashboard":

        st.subheader("📊 Dashboard Compras")
        st.dataframe(df.head(), use_container_width=True)

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
