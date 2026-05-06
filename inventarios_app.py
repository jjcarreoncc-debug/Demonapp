import streamlit as st
import pandas as pd
import base64
import os

# =========================
# CSS
# =========================
def aplicar_css():
    st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 70px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        background-color: #1f77b4;
        color: white;
    }
    div.stButton > button:hover {
        background-color: #145a86;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# FONDO
# =========================
def set_bg():
    if not os.path.exists("imagen8.png"):
        return

    with open("imagen8.png", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(
            rgba(255,255,255,0.85),
            rgba(255,255,255,0.85)
        ),
        url("data:image/png;base64,{encoded}");
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================
# PROCESO
# =========================
def procesar_datos(productos, movimientos, inventario):

    movimientos["TIPO"] = movimientos["TIPO"].astype(str).str.upper().str.strip()

    movimientos["ENTRADA"] = movimientos["CANTIDAD"].where(movimientos["TIPO"] == "COMPRA", 0)
    movimientos["SALIDA"] = movimientos["CANTIDAD"].where(movimientos["TIPO"] == "VENTA", 0)

    stock = movimientos.groupby("NUMERO_PRODUCTO")[["ENTRADA", "SALIDA"]].sum().reset_index()
    stock["STOCK"] = stock["ENTRADA"] - stock["SALIDA"]

    df = stock.merge(productos, on="NUMERO_PRODUCTO", how="left")
    df = df.merge(inventario, on="NUMERO_PRODUCTO", how="left")

    return df

# =========================
# MÉTRICAS (NUEVO 🔥)
# =========================
def calcular_metricas(df):

    metricas = {}

    metricas["total_stock"] = int(df["STOCK"].sum())
    metricas["criticos"] = df[df["STOCK"] < df["STOCK_MIN"]].shape[0]
    metricas["sobrestock"] = df[df["STOCK"] > df["STOCK_MAX"]].shape[0]
    metricas["rotacion"] = df["SALIDA"].sum() / df["ENTRADA"].sum() if df["ENTRADA"].sum() != 0 else 0
    metricas["ganancia"] = (df["SALIDA"] * 0.3).sum()

    return metricas

# =========================
# DASHBOARD GENERAL
# =========================
def dashboard_general(df):

    st.title("📊 Dashboard General")

    m = calcular_metricas(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Stock", f"{m['total_stock']:,}")
    c2.metric("🚨 Críticos", m["criticos"])
    c3.metric("⚠️ Sobrestock", m["sobrestock"])
    c4.metric("📈 Rotación", f"{m['rotacion']:.2f}")

    c5, c6 = st.columns(2)
    c5.metric("💰 Ganancia", f"${m['ganancia']:,.0f}")
    c6.metric("📊 Productos", len(df))

    if st.button("🔙 Volver"):
        st.session_state.inv_vista = "menu"
        st.rerun()

# =========================
# APP PRINCIPAL
# =========================
def inventarios_app():

    aplicar_css()
    set_bg()

    st.title("📊 Inventarios")

    # CARGA
    archivo_prod = st.file_uploader("📦 Productos", type=["xlsx"], key="prod")
    archivo_mov = st.file_uploader("📊 Movimientos", type=["xlsx"], key="mov")
    archivo_inv = st.file_uploader("🏭 Inventario", type=["xlsx"], key="inv")

    if archivo_prod:
        st.session_state.productos = pd.read_excel(archivo_prod)

    if archivo_mov:
        st.session_state.movimientos = pd.read_excel(archivo_mov)

    if archivo_inv:
        st.session_state.inventario = pd.read_excel(archivo_inv)

    productos = st.session_state.get("productos")
    movimientos = st.session_state.get("movimientos")
    inventario = st.session_state.get("inventario")

    if productos is None or movimientos is None or inventario is None:
        st.warning("⚠️ Carga los 3 archivos")
        return

    df = procesar_datos(productos, movimientos, inventario)

    if "inv_vista" not in st.session_state:
        st.session_state.inv_vista = "menu"

    # MENÚ
    if st.session_state.inv_vista == "menu":

        c1, c2, c3, c4, c5 = st.columns(5)

        if c1.button("General"):
            st.session_state.inv_vista = "dash1"
            st.rerun()

        if c2.button("Críticos"):
            st.session_state.inv_vista = "dash2"
            st.rerun()

        if c3.button("Sobrestock"):
            st.session_state.inv_vista = "dash3"
            st.rerun()

        if c4.button("Rotación"):
            st.session_state.inv_vista = "dash4"
            st.rerun()

        if c5.button("IA"):
            st.session_state.inv_vista = "dash5"
            st.rerun()

        return

    # DASHBOARD
    if st.session_state.inv_vista == "dash1":
        dashboard_general(df)
