import streamlit as st
import pandas as pd


import base64

import base64
import os

def set_bg():
    
    if not os.path.exists("imagen8.png"):
        st.warning("No se encontró fondo.png")
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
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

# 👇 ESTO ES CLAVE
set_bg()
def inventarios_app():

# =========================
# 1. CARGA DE ARCHIVOS
# =========================
    st.markdown("### 📂 Carga de archivos")

    archivo_prod = st.file_uploader("📦 Productos", type=["xlsx"], key="prod_file")
    archivo_mov = st.file_uploader("📊 Movimientos", type=["xlsx"], key="mov_file")
    archivo_inv = st.file_uploader("🏭 Inventario", type=["xlsx"], key="inv_file")

# =========================
# 2. GUARDAR EN SESSION
# =========================
    if archivo_prod:
        df_prod = pd.read_excel(archivo_prod)
        df_prod.columns = df_prod.columns.str.strip()
        st.session_state.productos = df_prod

    if archivo_mov:
        df_mov = pd.read_excel(archivo_mov)
        df_mov.columns = df_mov.columns.str.strip()
        st.session_state.movimientos = df_mov

    if archivo_inv:
        df_inv = pd.read_excel(archivo_inv)
        df_inv.columns = df_inv.columns.str.strip()
        st.session_state.inventario = df_inv


# =========================
# PASO 2 - VALIDAR DATOS
# =========================
productos = st.session_state.get("productos")
movimientos = st.session_state.get("movimientos")
inventario = st.session_state.get("inventario")

def inventarios_app():

    # =========================
    # BLOQUEO SI NO HAY DATA
    # =========================
    if not st.session_state.get("data_ready", False):
        st.warning("⚠️ Primero debes cargar los archivos en el módulo de Carga")
        st.stop()

    # 👇 A PARTIR DE AQUÍ YA PUEDES USAR LOS DATOS
    productos = st.session_state.get("productos")
    movimientos = st.session_state.get("movimientos")
    inventario = st.session_state.get("inventario")

# =========================
# PASO 3 - CONTROL SUBMENÚ
# =========================
if "inv_vista" not in st.session_state:
    st.session_state.inv_vista = "menu"


# =========================
# MENÚ DASHBOARDS
# =========================
if st.session_state.inv_vista == "menu":

    st.title("📊 Inventarios")

    c1, c2, c3, c4, c5 = st.columns(5)

    if c1.button("General"):
        st.session_state.inv_vista = "dash1"

    if c2.button("Críticos"):
        st.session_state.inv_vista = "dash2"

    if c3.button("Sobrestock"):
        st.session_state.inv_vista = "dash3"

    if c4.button("Rotación"):
        st.session_state.inv_vista = "dash4"

    if c5.button("IA"):
        st.session_state.inv_vista = "dash5"

    st.stop()

# =========================
# 5. PROCESAMIENTO
# =========================
    movimientos["TIPO"] = movimientos["TIPO"].astype(str).str.upper().str.strip()

    movimientos["ENTRADA"] = movimientos["CANTIDAD"].where(movimientos["TIPO"] == "COMPRA", 0)
    movimientos["SALIDA"] = movimientos["CANTIDAD"].where(movimientos["TIPO"] == "VENTA", 0)

    stock = movimientos.groupby("NUMERO_PRODUCTO")[["ENTRADA", "SALIDA"]].sum().reset_index()
    stock["STOCK"] = stock["ENTRADA"] - stock["SALIDA"]

    df = stock.merge(productos, on="NUMERO_PRODUCTO", how="left")
    df = df.merge(inventario, on="NUMERO_PRODUCTO", how="left")

# =========================
# 6. KPIs
# =========================
    total_stock = int(df["STOCK"].sum())
    criticos = df[df["STOCK"] < df["STOCK_MIN"]].shape[0]
    sobrestock = df[df["STOCK"] > df["STOCK_MAX"]].shape[0]
    rotacion = (df["SALIDA"].sum() / df["STOCK"].sum()) if df["STOCK"].sum() != 0 else 0

# =========================
# 7. DASHBOARD SIMPLE
# =========================
    st.markdown("## 📊 KPIs de Inventario")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📦 Stock Total", f"{total_stock:,}")
    c2.metric("🚨 Críticos", criticos)
    c3.metric("⚠️ Sobrestock", sobrestock)
    c4.metric("📈 Rotación", f"{rotacion:.2f}")

    st.markdown("## 📋 Detalle Inventario")
    st.dataframe(df)
