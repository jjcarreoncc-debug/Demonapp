import streamlit as st
import pandas as pd
import plotly.express as  px 
import sqlite3# 
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
import hashlib
import streamlit as st
from datetime import datetime
from PIL import Image
from inventarios_app import inventarios_app
from carga_app import carga_app
from compras_app import compras_app
from logistica_app import logistica_app
from wms_app import wms_app
from mantenimiento_app import mantenimiento_app
#st.set_page_config(page_title="Dashbo ard Ejecutivo", layout="wide")
from mantenimiento_auditoria_app import registrar_auditoria
from menu_dinamico import sidebar_dinamico
from diagnostico_tablas_app import diagnostico_tablas_app
from sidebar_sge import sidebar_sge

from seed_data import seed_data
from auth_app import login_app, logout_app
from ui_components import card_kpi, mostrar_logos
import crear_tablas
#from database import get_connection
from sidebar_sge import sidebar_sge



# ------------------------!
# CONFIG
#
# ------------------------
#st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")
st.set_page_config(
    page_title=" Ejecutivo",
    layout="wide")
# ------------------------
# LOGIN CONFIG
# ------------------------

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if "nombre" not in st.session_state:
    st.session_state.nombre = None

if "rol" not in st.session_state:
    st.session_state.rol = None



# =========================
# LOGIN
# =========================

# LOGIN TEMPORAL DESACTIVADO

st.session_state.autenticado = True
st.session_state.usuario = "admin"
st.session_state.rol = "Administrador"
#if not st.session_state.autenticado:
 #   login_app()
 #   st.stop()
#logout_app()

# =========================
# NUEVO SIGEM PRINCIPAL
# =========================

ruta = sidebar_dinamico()

if ruta == "inicio":
    st.empty()

elif ruta == "inventarios":
    st.title("📦 Inventarios")
    inventarios_app()

elif ruta == "compras":
    st.title("🛒 Compras")
    compras_app()
    
elif ruta == "logistica":
    st.title("🚚 Logística")
    logistica_app()
elif ruta == "wms":
    st.title("🏬 WMS")
    
    wms_app()
elif ruta == "mantenimiento":
    st.title("🛠️ Mantenimiento")
    mantenimiento_app()   

else:
    st.warning(f"Ruta no configurada: {ruta}")

st.stop()

# =========================
# SELECTOR DE FLUJO
# =========================

st.sidebar.markdown("---")

flujo = st.sidebar.radio(
    "Modo de trabajo",
    ["Flujo actual", "Nuevo SIGEM"],
    key="flujo_sistema"
)

# =========================
# NUEVO SIGEM
# =========================

if "ruta" not in st.session_state:
    st.session_state.ruta = "Inicio"
if "rol" not in st.session_state:
    st.session_state.rol = "Usuario"    

# =========================
# ESTILOS (LIMPIO + IMAGEN)
# =========================
if flujo == "Nuevo SIGEM":

    ruta = sidebar_dinamico()

    if ruta == "inicio":
        pass

    elif ruta == "datos_maestros":
        st.title("📘 Datos Maestros")

    elif ruta == "Minventarios":
        

        from sidebar_inventarios import sidebar_inventarios
        
        opcion_inv = sidebar_inventarios()
        
        st.title("📦 Inventarios")
        
        st.write("Opción seleccionada:", opcion_inv)
        
        st.stop()
        
    elif ruta == "compras":
        st.title("🛒 Compras")

    elif ruta == "ventas":
        st.title("💰 Ventas")

    elif ruta == "logistica":
        st.title("🚚 Logística")
        
    st.stop() 
    
st.markdown("""
<style>

/* Fondo principal */
.stApp {
    background-color: #f2f2f2;
}

/* Contenedor principal */
.block-container {
    background-color: #f2f2f2;
    padding-top: 1rem;
}

/* Sidebar (lo dejamos oscuro para contraste) */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1f4e63, #2c6e8f);
}

/* Tarjetas (métricas, contenedores) */
[data-testid="metric-container"],
div.stDataFrame,
div.stPlotlyChart {
    background-color: white;
    border-radius: 12px;
    padding: 10px;
}

/* Títulos */
h1, h2, h3 {
    color: #1f4e63;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* ===== SIDEBAR BASE ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1f3b4d 0%, #2e6f95 100%);
    padding-top: 20px;
}

/* ===== BOTONES ===== */
div.stButton > button {
    width: 100%;
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff !important;
    border: none;
    border-radius: 14px;
    padding: 12px 14px;
    font-size: 15px;
    font-weight: 500;
    text-align: left;
    transition: all 0.25s ease;
    backdrop-filter: blur(6px);
}

/* Hover */
div.stButton > button:hover {
    background: rgba(255, 255, 255, 0.18);
    transform: translateX(5px);
    color: #ffffff !important;
}

/* Activo (simulado con focus) */
div.stButton > button:focus {
    background: #ffffff;
    color: #1f3b4d !important;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* ===== TEXTO GENERAL ===== */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* ===== TÍTULO ===== */
.sidebar-title {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 20px;
    padding-left: 10px;
}

/* ===== SEPARADORES ===== */
.sidebar-divider {
    height: 1px;
    background: rgba(255,255,255,0.2);
    margin: 15px 0;
}

/* ===== ICONOS ESPACIADO ===== */
button p {
    margin: 0;
}

/* ===== SCROLLBAR ===== */
section[data-testid="stSidebar"]::-webkit-scrollbar {
    width: 6px;
}
section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.3);
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* ===== SIDEBAR ===== */
/* tu código anterior */

/* ===== BOTONES ===== */
/* tu código anterior */

/* ===== INPUTS (PEGA AQUÍ LO NUEVO) ===== */
label {
    color: #ffffff !important;
    font-weight: 600;
}

div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.9) !important;
    color: #1f2d3d !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] span {
    color: #1f2d3d !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* 🔥 FORZAR COLOR DE TEXTO EN INPUTS */
input, textarea {
    color: black !important;
}

/* LABELS */
label {
    color: #1f4e63 !important;
    font-weight: 600;
}

/* PLACEHOLDER (texto dentro del input) */
::placeholder {
    color: #888 !important;
}

/* BOTONES LOGIN */
button {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)
# =========================
# INICIALIZAR ESTADO
# =========================
if "vista" not in st.session_state:
    st.session_state.vista = "inicio"




# =====================================
# CSS DEL SISTEMA
# =====================================

st.markdown("""
<style>

/* TU CSS NORMAL DEL DASHBOARD */

.stApp {
    background-color: #f2f2f2;
}

.block-container {
    background-color: #f2f2f2;
}

</style>
""", unsafe_allow_html=True)


st.sidebar.success(
    f"Usuario: {st.session_state.nombre}"
)

st.sidebar.info(
    f"Rol: {st.session_state.rol}"
)

# ------------------------
# LOGO
# ------------------------
mostrar_logos()

# ------------------------
# USUARIO ACTUAL
# ------------------------
usuario_actual = {
    "usuario": st.session_state.usuario,
    "nombre": st.session_state.nombre,
    "rol": st.session_state.rol
}
  
  

    

# ------------------------
# INICIALIZAR MENU
# ------------------------
if "ruta" not in st.session_state:
    st.session_state.ruta = "Inicio"


# =========================
# INICIO
# =========================
def pantalla_inicio():
    st.title("🏠 Inicio")


# =========================
# SIDEBAR DINAMICO PARA HACER FUNCION CON NUEVO BLOQUE 
# =========================

ruta = sidebar_dinamico()

if not ruta:
    st.stop()

if ruta == "inicio":
    st.title("🏠 Inicio")
    st.info("Selecciona un módulo del menú lateral para comenzar.")

elif ruta == "datos_maestros":
    st.title("📘 Datos Maestros")

elif ruta == "inventarios":

    from sidebar_inventarios import sidebar_inventarios

    opcion_inv = sidebar_inventarios()

    
    st.write("Opción seleccionada:", opcion_inv)
    
    st.title("📦 Inventarios")

elif ruta == "compras":
    st.title("🛒 Compras")

elif ruta == "ventas":
    st.title("💰 Ventas")

elif ruta == "logistica":
    st.title("🚚 Logística")

else:
    st.warning(f"Ruta no configurada: {ruta}") #

st.stop()

######
### TEMPORALMENTE
#####
if "ultima_ruta_auditada" not in st.session_state:
    st.session_state.ultima_ruta_auditada = None

if st.session_state.ultima_ruta_auditada != ruta:

    registrar_auditoria(
        st.session_state.usuario,
        ruta,
        "ACCESO_MODULO",
        f"Ingresó al módulo {ruta}"
    )


# =========================
# FUNCION DE APP DE INVENTARIOS
# =========================
def dashboard():   # 👈 AQUÍ VA TU FUNCIÓN

    st.title("📊 Dashboard")

    if "archivo" not in st.session_state:
        st.warning("⚠️ Carga un archivo")
        return

    df = pd.read_excel(st.session_state.archivo)

    df.columns = df.columns.str.strip().str.upper()

    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
        df = df.dropna(subset=["FECHA"])
        df["AÑO"] = df["FECHA"].dt.year
        df["MES"] = df["FECHA"].dt.month_name()

    if "VENTAS_CANTIDAD" in df.columns:
        df["VENTAS"] = df["VENTAS_CANTIDAD"]
        df["GANANCIA"] = df["VENTAS"] * 0.3

    st.dataframe(df.head())

