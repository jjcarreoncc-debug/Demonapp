import streamlit as st
import pandas as pd
import base64
import os
def inventarios_app():

    # 🔥 CSS AQUÍ
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
        box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
    }

    div.stButton > button:hover {
        background-color: #145a86;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown("""
<style>

/* 🔥 TEXTO DE BOTONES MÁS OSCURO */
div.stButton > button {
    color: #1f2d3d !important;   /* gris oscuro */
    font-weight: 700;
    font-size: 16px;
}

/* 🔥 HOVER */
div.stButton > button:hover {
    color: #000000 !important;
}

/* 🔥 CUANDO ESTÁ ACTIVO */
div.stButton > button:focus {
    color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* 🔥 TEXTO DENTRO DE COLUMNAS */
div[data-testid="column"] p {
    color: black !important;
    font-weight: 700;
    font-size: 16px;
    text-align: center;
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
    # 🔥 AQUÍ GENERAS df UNA SOLA VEZ
    df = procesar_datos(productos, movimientos, inventario)

    if "inv_vista" not in st.session_state:
        st.session_state.inv_vista = "dash1"

    if st.session_state.inv_vista == "dash1":
        dashboard_general(df)

    # =========================
    # 3. MENÚ DASHBOARDS
    # =========================
    if "inv_vista" not in st.session_state:
        st.session_state.inv_vista = "menu"

    if st.session_state.inv_vista == "menu":
        c1, c2, c3, c4, c5 = st.columns(5, gap="large")  
        c1, c2, c3, c4, c5 = st.columns(5)

        if c1.button("General"):
            st.session_state.inv_vista = "dash1"
            def dashboard_general(df):
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

        st.stop()

    # 🔙 Volver
    if st.button("🔙 Volver"):
        st.session_state.inv_vista = "menu"
        st.rerun() 
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
# =========================
# DASHBOARD GENERAL
# =========================
def dashboard_general(df):

    st.title("📊 Dashboard General")

    total_stock = int(df["STOCK"].sum())
    criticos = df[df["STOCK"] < df["STOCK_MIN"]].shape[0]
    sobrestock = df[df["STOCK"] > df["STOCK_MAX"]].shape[0]
    rotacion = df["SALIDA"].sum() / df["ENTRADA"].sum() if df["ENTRADA"].sum() != 0 else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📦 Stock", f"{total_stock:,}")
    c2.metric("🚨 Críticos", criticos)
    c3.metric("⚠️ Sobrestock", sobrestock)
    c4.metric("📈 Rotación", f"{rotacion:.2f}")
# =========================
# MAIN APP
# =========================
def inventarios_app():

    productos = st.session_state.get("productos")
    movimientos = st.session_state.get("movimientos")
    inventario = st.session_state.get("inventario")

    if productos is None or movimientos is None or inventario is None:
        st.warning("⚠️ Carga los archivos primero")
        return

    df = procesar_datos(productos, movimientos, inventario)

    if "inv_vista" not in st.session_state:
        st.session_state.inv_vista = "dash1"

    if st.session_state.inv_vista == "dash1":
        dashboard_general(df)
    
    return df
    
