import streamlit as st
import pandas as pd
import base64
import os

# =========================
# FONDO
# =========================
def set_bg():
    if not os.path.exists("imagen8.png"):
        return

    with open("imagen8.png", "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(
            rgba(255,255,255,0.85),
            rgba(255,255,255,0.85)
        ),
        url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================
# APP INVENTARIOS
# =========================
def inventarios_app():

    set_bg()

    st.title("📊 Inventarios")

    # =========================
    # 1. CARGA
    # =========================
    archivo_prod = st.file_uploader("📦 Productos", type=["xlsx"], key="prod")
    archivo_mov = st.file_uploader("📊 Movimientos", type=["xlsx"], key="mov")
    archivo_inv = st.file_uploader("🏭 Inventario", type=["xlsx"], key="inv")

    if archivo_prod:
        df = pd.read_excel(archivo_prod)
        df.columns = df.columns.str.strip()
        st.session_state.productos = df

    if archivo_mov:
        df = pd.read_excel(archivo_mov)
        df.columns = df.columns.str.strip()
        st.session_state.movimientos = df

    if archivo_inv:
        df = pd.read_excel(archivo_inv)
        df.columns = df.columns.str.strip()
        st.session_state.inventario = df

    productos = st.session_state.get("productos")
    movimientos = st.session_state.get("movimientos")
    inventario = st.session_state.get("inventario")

    # =========================
    # 2. VALIDACIÓN
    # =========================
    if productos is None or movimientos is None or inventario is None:
        st.warning("⚠️ Carga los 3 archivos")
        return

    st.success("✅ Archivos cargados")

    # =========================
    # 3. MENÚ DASHBOARDS
    # =========================
    if "inv_vista" not in st.session_state:
        st.session_state.inv_vista = "menu"

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

    # 🔙 Volver
    if st.button("🔙 Volver"):
        st.session_state.inv_vista = "menu"
        st.rerun()

    # =========================
    # 4. PROCESAMIENTO
    # =========================
    movimientos["TIPO"] = movimientos["TIPO"].astype(str).str.upper().str.strip()

    movimientos["ENTRADA"] = movimientos["CANTIDAD"].where(movimientos["TIPO"] == "COMPRA", 0)
    movimientos["SALIDA"] = movimientos["CANTIDAD"].where(movimientos["TIPO"] == "VENTA", 0)

    stock = movimientos.groupby("NUMERO_PRODUCTO")[["ENTRADA", "SALIDA"]].sum().reset_index()
    stock["STOCK"] = stock["ENTRADA"] - stock["SALIDA"]

    df = stock.merge(productos, on="NUMERO_PRODUCTO", how="left")
    df = df.merge(inventario, on="NUMERO_PRODUCTO", how="left")

    # =========================
    # 5. KPIs
    # =========================
    total_stock = int(df["STOCK"].sum())
    criticos = df[df["STOCK"] < df["STOCK_MIN"]].shape[0]
    sobrestock = df[df["STOCK"] > df["STOCK_MAX"]].shape[0]
    rotacion = (df["SALIDA"].sum() / df["STOCK"].sum()) if df["STOCK"].sum() != 0 else 0

    st.markdown("## 📊 KPIs")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stock", f"{total_stock:,}")
    c2.metric("Críticos", criticos)
    c3.metric("Sobrestock", sobrestock)
    c4.metric("Rotación", f"{rotacion:.2f}")

    st.dataframe(df)
