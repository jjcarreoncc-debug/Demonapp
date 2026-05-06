import streamlit as st
import pandas as pd
import base64
import os
from alertas_criticas import dashboard_criticos

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

def card_kpi(titulo, valor, color="#1f77b4"):

    st.markdown(f"""
    <div style="
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid {color};
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    ">
        <div style="font-size:18px; font-weight:600; color:#2c3e50;">
            {titulo}
        </div>
        <div style="font-size:30px; font-weight:700; color:{color}; margin-top:10px;">
            {valor}
        </div>
    </div>
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
# DETALLE DASHBOARD
# =========================
def dashboard_detalle(df):
    # TOP VENDIDOS
    st.subheader("🔥 Top Productos Más Vendidos")

    top = df.sort_values(
        "SALIDA",
        ascending=False
    ).head(10)

    st.bar_chart(
        top.set_index("NOMBRE_PRODUCTO")["SALIDA"]
    )

    # CRÍTICOS
    st.subheader("🚨 Productos Críticos")

    criticos = df[
        df["STOCK"] < df["STOCK_MIN"]
    ]

    st.dataframe(
        criticos[
            [
                "NUMERO_PRODUCTO",
                "NOMBRE_PRODUCTO",
                "STOCK",
                "STOCK_MIN"
            ]
        ]
    )

    # SEMÁFORO
    def estado_stock(row):

        if row["STOCK"] < row["STOCK_MIN"]:
            return "🔴 Crítico"

        elif row["STOCK"] > row["STOCK_MAX"]:
            return "🟠 Sobrestock"

        return "🟢 Normal"

    df["ESTADO"] = df.apply(
        estado_stock,
        axis=1
    )

    st.subheader("📦 Estado Inventario")

    st.dataframe(
        df[
            [
                "NOMBRE_PRODUCTO",
                "STOCK",
                "ESTADO"
            ]
        ]
    )
# =========================
# DASHBOARD GENERAL
# =========================
def dashboard_general(df):
 

    

    st.title("📊 Dashboard General")

    m = calcular_metricas(df)

    # 🔥 FILA 1
    c1, c2 = st.columns(2)

    with c1:
        card_kpi("📦 Stock Total", f"{m['total_stock']:,}", "#1f77b4")
           
    with c2:
        card_kpi("🚨 Críticos", m["criticos"], "#e74c3c")

    # 🔥 FILA 2
    c3, c4 = st.columns(2)

    with c3:
        card_kpi("⚠️ Sobrestock", m["sobrestock"], "#f39c12")

    with c4:
        card_kpi("📈 Rotación", f"{m['rotacion']:.2f}", "#2ecc71")

    # 🔥 FILA 3
    c5, c6 = st.columns(2)

    with c5:
        card_kpi("💰 Ganancia", f"${m['ganancia']:,.0f}", "#27ae60")

    with c6:
        card_kpi("📊 Productos", len(df), "#34495e")
        
    # 🔙 Volver
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

           # DASHBOARD
    if st.session_state.inv_vista == "dash1":
        dashboard_general(df)
