import streamlit as st
import pandas as pd
import plotly.express as  px 
import sqlite3# 
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher

import hashlib
from datetime import datetime
from PIL import Image

# ------------------------
# CONFIG

# ------------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")
st.set_page_config(
    page_title=" Ejecutivo",
    layout="wide")
if "menu" not in st.session_state:
    st.session_state.menu = "Inicio"
if "rol" not in st.session_state:
    st.session_state.rol = "Usuario"    

# =========================
# ESTILOS (LIMPIO + IMAGEN)
# =========================

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
# ------------------------
# BASE DE DATOS
# ------------------------
conn = sqlite3.connect("data.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    rol TEXT,
    estado TEXT,
    fecha_creacion TEXT,
    area TEXT,
    transacciones TEXT
)
""")
conn.commit()

# ------------------------
# LOGIN CONFIG
# ------------------------
passwords = ["1234", "abcd"]
hashed_passwords = Hasher(passwords).generate()

credentials = {
    "usernames": {
        "admin": {"name": "Admin", "password": hashed_passwords[0]},
        "ventas": {"name": "Ventas", "password": hashed_passwords[1]}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "mi_dashboard",
    "abcdef",
    cookie_expiry_days=1
)

# ------------------------
# LOGO
# ------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("LOOGO-TIDS-CONSULTING (2).jpg", width=200)

# ------------------------
# LOGIN
# ------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    name, authentication_status, username = authenticator.login("Login", location="main")

# ------------------------
# CONTROL LOGIN
# ------------------------

# =========================
# LOGIN CONTROL
# =========================

if authentication_status is False:
    st.error("Usuario o contraseña incorrectos")

    # 🔥 LOGIN SIEMPRE BLANCO
    st.markdown("""
    <style>
    .stApp {
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.stop()


if authentication_status is None:

    # 🔥 LOGIN SIEMPRE BLANCO
    st.markdown("""
    <style>
    .stApp {
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2,6])
    with col2:
        img = Image.open("imagen7.png")
        st.image(img, width=2000)

    st.stop()


# =========================
# DESPUÉS DE LOGIN → GRIS
# =========================
if authentication_status:

    st.markdown("""
    <style>
    .stApp {
        background-color: #f2f2f2;
    }
    </style>
    """, unsafe_allow_html=True)
# ------------------------
# FUNCIONES USUARIOS
# ------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def obtener_usuarios():
    return pd.read_sql("SELECT * FROM usuarios", conn)

def crear_usuario(username, password, nombre, rol, area, transacciones):
    try:
        trans_str = ",".join(transacciones)
        conn.execute("""
        INSERT INTO usuarios (username, password, nombre, rol, estado, fecha_creacion, area, transacciones)
        VALUES (?, ?, ?, ?, 'Activo', ?, ?, ?)
        """, (
            username,
            hash_password(password),
            nombre,
            rol,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            area,
            trans_str
        ))
        conn.commit()
        return True
    except Exception as e:
        return str(e)

def desactivar_usuario(user_id):
    conn.execute("UPDATE usuarios SET estado='Inactivo' WHERE id=?", (user_id,))
    conn.commit()

# ------------------------
# USUARIO ACTUAL
# ------------------------
df_users = obtener_usuarios()

usuario_actual = df_users[df_users["username"] == username]
if not usuario_actual.empty:
    usuario_actual = usuario_actual.iloc[0]
else:
    usuario_actual = None
    
# =========================
# MANTENIMIENTO
# =========================

if st.session_state.menu == "Mantenimiento":
    st.title("🛠️ Mantenimiento de Usuarios")

    # Validación de rol
    if st.session_state.rol != "Admin":
        st.warning("⛔ No tienes permisos")
        st.stop()

    # =========================
    # DATA (MEMORIA)
    # =========================
    if "usuarios" not in st.session_state:
        st.session_state.usuarios = [
            {"usuario": "admin", "nombre": "Administrador", "rol": "Admin", "estado": "Activo"},
            {"usuario": "user1", "nombre": "Usuario Demo", "rol": "Usuario", "estado": "Activo"}
        ]

    usuarios = st.session_state.usuarios

    # =========================
    # USUARIOS
    # =========================
    st.markdown("### 👥 Usuarios")

    df_users = pd.DataFrame(usuarios)
    st.dataframe(df_users, use_container_width=True)

    # =========================
    # CREAR USUARIO
    # =========================
    st.markdown("### ➕ Crear usuario")

    col1, col2 = st.columns(2)

    with col1:
        nuevo_usuario = st.text_input("Usuario", key="u_usuario")
        nombre = st.text_input("Nombre", key="u_nombre")

    with col2:
        rol_nuevo = st.selectbox("Rol", ["Admin", "Usuario"], key="u_rol")
        estado = st.selectbox("Estado", ["Activo", "Inactivo"], key="u_estado")

    if st.button("Guardar usuario"):
        if nuevo_usuario and nombre:
            usuarios.append({
                "usuario": nuevo_usuario,
                "nombre": nombre,
                "rol": rol_nuevo,
                "estado": estado
            })
            st.success("✅ Usuario creado")

    # =========================
    # ELIMINAR USUARIO
    # =========================
    st.markdown("### ❌ Eliminar usuario")

    lista = [u["usuario"] for u in usuarios]
    user_del = st.selectbox("Selecciona usuario", lista, key="del_user")

    if st.button("Eliminar usuario"):
        st.session_state.usuarios = [
            u for u in usuarios if u["usuario"] != user_del
        ]
        st.success("🗑️ Usuario eliminado")
   
# ------------------------
# SIDEBAR
# ------------------------
st.markdown("""
<style>

/* 🔥 SUBIR TODO EL CONTENIDO DEL SIDEBAR */
section[data-testid="stSidebar"] .block-container {
    padding-top: 0rem !important;
    margin-top: -20px !important;
}

/* 🔥 QUITAR ESPACIO DEL TÍTULO */
section[data-testid="stSidebar"] h1 {
    margin-top: 0px !important;
    padding-top: 0px !important;
}

/* 🔥 AJUSTAR TEXTO BIENVENIDO */
section[data-testid="stSidebar"] p {
    margin-top: 5px !important;
}

</style>
""", unsafe_allow_html=True)
with st.sidebar:

    # 👇 CSS aquí arriba
    st.markdown(""" ... """, unsafe_allow_html=True)

    st.title("📌 Navegación")
    st.markdown(f"👋 **Bienvenido {name}**")
# ------------------------
    # ROL
    # ------------------------
    rol = "Admin" if username == "admin" else "Usuario"
    st.session_state.rol = rol
    

    st.markdown("---")

    authenticator.logout("Cerrar sesión", "sidebar")

    
    # OPCIONES
    # ------------------------
    if st.session_state.rol == "Admin":
        opciones = ["Inicio", "Dashboard", "Mantenimiento"]
    else:
        opciones = ["Inicio", "Dashboard"]

    # ------------------------
    # INICIALIZAR MENU
    
    # ------------------------
    if "menu" not in st.session_state:
        st.session_state.menu = "Inicio"

    # ------------------------
    # MENU
    # ------------------------
    menu = st.radio(
        "Menú",
        opciones,
        index=opciones.index(st.session_state.menu)
    )

    st.session_state.menu = menu
    # =========================
    # FILTROS SOLO EN DASHBOARD
    # =========================
    
    # ------------------------
    # MOSTRAR FILTROS (solo en dashboard)
    # ------------------------
    if st.session_state.menu == "Dashboard":

        st.markdown("---")
        st.markdown("### 🎯 Filtros")

        # valores por defecto
        año = "Todos"
        mes = "Todos"
        pais = "Todos"
        region = "Todos"
        producto = []

        if "archivo" in st.session_state:

            df_temp = pd.read_excel(st.session_state.archivo)
            df_temp.columns = df_temp.columns.str.strip()

            df_temp["Fecha"] = pd.to_datetime(df_temp["Fecha"], errors="coerce")
            df_temp = df_temp.dropna(subset=["Fecha"])

            df_temp["Año"] = df_temp["Fecha"].dt.year
            df_temp["Mes"] = df_temp["Fecha"].dt.month_name()

            # AÑO
            año = st.selectbox("📅 Año", ["Todos"] + sorted(df_temp["Año"].unique()), key="año")

            # MES
            mes = st.selectbox("📆 Mes", ["Todos"] + sorted(df_temp["Mes"].unique()), key="mes")
            
            col_pais = next((c for c in df_temp.columns if "pais" in c.lower()), None)
            # PAÍS
            #pais = st.selectbox(
            #    "🌎 País",    
            #    ["Todos"] + sorted(df_temp["Pais"].dropna().unique()),
            #    key="filtro_pais"
            #)

            # REGIÓN
            df_region = df_temp if pais == "Todos" else df_temp[df_temp["Pais"] == pais]

            #region = st.selectbox(
            #    "📍 Región",
            #    ["Todos"] + sorted(df_region["Region"].dropna().unique()),
            #    key="filtro_region"
            #)
            # PRODUCTO
            df_producto = df_region if region == "Todos" else df_region[df_region["Region"] == region]
            # =========================
            # PRODUCTO (CORRECTO)
            # =========================
            # =========================
            col_producto = next((c for c in df_temp.columns if "PRODUCTO" in c), None)
            
            if col_producto:
            
                opciones_producto = ["Todos"] + sorted(df_temp[col_producto].dropna().astype(str).unique())
            
                # limpiar estado viejo
                if isinstance(st.session_state.get("filtro_producto"), list):
                    st.session_state["filtro_producto"] = "Todos"
            
                #producto = st.selectbox(
                #    "📦 Producto",
                #    options=opciones_producto,
                #    key="filtro_producto"
                #)
            
                if producto != "Todos":
                    df_temp = df_temp[df_temp[col_producto].astype(str) == producto]
            else:
                st.warning("⚠️ No se encontró columna de producto")
            
# =========================
# INICIO
# =========================
# =========================
# CONTROL DE VISTA
# =========================
if "vista" not in st.session_state:
    st.session_state.vista = "inicio"
# =========================
# INICIO
# =========================
if "vista" not in st.session_state:
    st.session_state.vista = "inicio"
if menu == "Inicio":

    st.title("🏠 Inicio")

    archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

    if archivo:
        st.session_state.archivo = archivo
        st.success("✅ Archivo cargado correctamente")

        # 🔥 BOTÓN VOLVER AL MENÚ
        if st.button("🔙 Volver al menú de navegación"):
            st.session_state.menu = "Dashboard"  # o "Inicio" si quieres quedarte
            st.rerun()

    elif "archivo" in st.session_state:
        st.info("📊 Ya hay un archivo cargado")

        # 🔥 BOTÓN TAMBIÉN SI YA EXISTE ARCHIVO
        if st.button("🔙 Ir al Dashboard"):
            st.session_state.menu = "Dashboard"
            st.rerun()

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":

    # =========================
    # TOMAR VALORES DEL SIDEBAR
    # =========================
    año = st.session_state.get("filtro_año", "Todos")
    mes = st.session_state.get("filtro_mes", "Todos")
    pais = st.session_state.get("filtro_pais", "Todos")
    region = st.session_state.get("filtro_region", "Todos")
    producto = st.session_state.get("filtro_producto", [])

    st.header("📊 Dashboard Ejecutivo")

    archivo = st.session_state.get("archivo")

    if not archivo:
        st.warning("⚠️ Primero carga un archivo en Inicio")
    else:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()
        # =========================
# CREAR FECHA Y PERIODO (OBLIGATORIO AQUÍ)
# =========================
        col_fecha = next((c for c in df.columns if "FECHA" in c), None)
        
        if not col_fecha:
            st.error("❌ No se encontró columna FECHA")
            st.stop()
        
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
        df = df.dropna(subset=[col_fecha])
        
        df["PERIODO"] = df[col_fecha].dt.to_period("M").astype(str) 
        # ------------------------
        # LIMPIEZA
        # ------------------------
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df = df.dropna(subset=["Fecha"])

        for col in ["Ventas_Cantidad", "Precio_Venta", "Costos_Venta"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # ------------------------
        # CAMPOS
        # ------------------------
        df["Año"] = df["Fecha"].dt.year
        df["Mes"] = df["Fecha"].dt.month_name()

        # MÉTRICAS
        df["Ventas"] = df["Ventas_Cantidad"] * df["Precio_Venta"]
        df["Costos"] = df["Ventas_Cantidad"] * df["Costos_Venta"]
        df["Ganancia"] = df["Ventas"] - df["Costos"]

        # ------------------------
        # FILTRADO
        # ------------------------
        df_filtrado = df.copy()

        if año != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Año"] == año]

        if mes != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Mes"] == mes]

        # PAIS (ultra robusto)
        col_pais = next((c for c in df_filtrado.columns if "pais" in c.lower()), None)
    
        if pais != "Todos" and col_pais:
            df_filtrado[col_pais] = df_filtrado[col_pais].astype(str).str.strip().str.lower()
            pais = str(pais).strip().lower()
            df_filtrado = df_filtrado[df_filtrado[col_pais] == pais]
        
        col_region = next((c for c in df_filtrado.columns if "region" in c.lower()), None)
        if region != "Todos" and col_region:
            df_filtrado[col_region] = df_filtrado[col_region].astype(str).str.strip().str.lower()
            region = str(region).strip().lower()
            df_filtrado = df_filtrado[df_filtrado[col_region] == region]

        # PRODUCTO
        # PRODUCTO
        col_producto = next((
            c for c in df_filtrado.columns 
            if any(x in c.lower() for x in ["producto", "product", "item", "sku"])
        ), None)
        
        # 🔴 DEBUG (esto va justo debajo)
        if not col_producto:
            st.error("❌ No se encontró columna de producto")
            st.write("Columnas disponibles:", df_filtrado.columns.tolist())
            st.stop()
            st.write("COLUMNAS DEL ARCHIVO:", df_filtrado.columns.tolist())
           
        # ------------------------
        # RESULTADO
        # ------------------------
        if df_filtrado.empty:
            st.warning("⚠️ No hay datos con esos filtros")
        else:
            ventas_mes = df_filtrado.groupby("Mes")["Ventas"].sum().reset_index()

            st.subheader("📈 Ventas por Mes")
            st.bar_chart(ventas_mes.set_index("Mes"))
            st.write("🔍 Tamaño del dataframe filtrado:", df_f.shape)
            st.write("🔍 Columnas disponibles:", df_f.columns)
            st.dataframe(df_f.head())
            # ------------------------
            # KPIs
            # ------------------------
            col1, col2, col3 = st.columns(3)

            col1.metric("Ventas Totales", f"${df_filtrado['Ventas'].sum():,.0f}")
            col2.metric("Costos Totales", f"${df_filtrado['Costos'].sum():,.0f}")
            col3.metric("Ganancia", f"${df_filtrado['Ganancia'].sum():,.0f}")
elif menu == "Principal":

    st.header("📊 Dashboard Ejecutivo")

    # =========================
    # VALIDAR ARCHIVO
    # =========================
    archivo = st.session_state.get("archivo")

    if not archivo:
        st.warning("⚠️ Primero carga un archivo en Inicio")
        st.stop()

    # =========================
    # CARGA DATA
    # =========================
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip().str.upper()

    # =========================
    # VALIDAR FECHA
    # =========================
    col_fecha = next((c for c in df.columns if "FECHA" in c), None)

    if not col_fecha:
        st.error("❌ No se encontró columna FECHA")
        st.stop()

    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
    df = df.dropna(subset=[col_fecha])

    # =========================
    # CAMPOS BASE
    # =========================
    df["AÑO"] = df[col_fecha].dt.year
    df["MES"] = df[col_fecha].dt.month_name()
    df["PERIODO"] = df[col_fecha].dt.to_period("M").astype(str)

    # =========================
    # MÉTRICAS
    # =========================
    if all(c in df.columns for c in ["VENTAS_CANTIDAD", "PRECIO_VENTA", "COSTOS_VENTA"]):

        df["VENTAS"] = df["VENTAS_CANTIDAD"] * df["PRECIO_VENTA"]
        df["COSTOS"] = df["VENTAS_CANTIDAD"] * df["COSTOS_VENTA"]
        df["GANANCIA"] = df["VENTAS"] - df["COSTOS"]

    else:
        st.error("❌ Faltan columnas necesarias")
        st.stop()

    # =========================
    # COLUMNAS DINÁMICAS
    # =========================
    col_pais = next((c for c in df.columns if "PAIS" in c), None)
    col_region = next((c for c in df.columns if "REGION" in c), None)
    col_producto = next((c for c in df.columns if "PRODUCT" in c), None)

    # =========================
    # DRILL-DOWN SUPERIOR
    # =========================
    c1, c2, c3 = st.columns(3)

    with c1:
        opciones_pais = ["Todos"] + sorted(df[col_pais].dropna().astype(str).unique())
        pais = st.selectbox("🌎 País", opciones_pais)

    with c2:
        df_region = df if pais == "Todos" else df[df[col_pais].astype(str) == pais]
        opciones_region = ["Todos"] + sorted(df_region[col_region].dropna().astype(str).unique())
        region = st.selectbox("📍 Región", opciones_region)

    with c3:
        df_producto = df_region if region == "Todos" else df_region[df_region[col_region].astype(str) == region]
        opciones_producto = ["Todos"] + sorted(df_producto[col_producto].dropna().astype(str).unique())
        producto = st.selectbox("📦 Producto", opciones_producto)

    # =========================
    # FILTRADO FINAL
    # =========================
    df_f = df.copy()

    if pais != "Todos":
        df_f = df_f[df_f[col_pais].astype(str) == pais]

    if region != "Todos":
        df_f = df_f[df_f[col_region].astype(str) == region]

    if producto != "Todos":
        df_f = df_f[df_f[col_producto].astype(str) == producto]

    # =========================
    # VALIDAR DATA
    # =========================
    if df_f.empty:
        st.warning("⚠️ No hay datos con esos filtros")
        st.stop()

    # =========================
    # KPIs
    # =========================
    ventas = df_f["VENTAS"].sum()
    ganancia = df_f["GANANCIA"].sum()
    margen = (ganancia / ventas) * 100 if ventas != 0 else 0

    df_m = df_f.groupby("PERIODO")[["VENTAS"]].sum().reset_index()
    df_m = df_m.sort_values("PERIODO")

    variacion = 0
    if len(df_m) >= 2:
        v1 = df_m.iloc[-2]["VENTAS"]
        v2 = df_m.iloc[-1]["VENTAS"]
        if v1 != 0:
            variacion = (v2 - v1) / v1

    delta_color = "normal" if variacion >= 0 else "inverse"

    k1, k2, k3 = st.columns(3)

    k1.metric("💰 Ventas", f"${ventas:,.0f}", f"{variacion:.1%}", delta_color=delta_color)
    k2.metric("💵 Ganancia", f"${ganancia:,.0f}")
    k3.metric("📊 Margen", f"{margen:.1f}%")

    # =========================
    # GRÁFICA
    # =========================
    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_m["PERIODO"],
        y=df_m["VENTAS"],
        mode="lines+markers",
        name="Ventas"
    ))

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # TABLA
    # =========================
    st.subheader("🔍 Detalle")
    st.dataframe(df_f.head(), use_container_width=True)


# =========================
# MANTENIMIENTO
# =========================
elif menu == "Mantenimiento":
    st.title("🛠️ Mantenimiento de Usuarios")

# ------------------------
# DATA GLOBAL
# -----------------------
if "archivo" in st.session_state:

    df = pd.read_excel(st.session_state.archivo)

    # NORMALIZAR
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.upper()

    # FECHA
    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
        df = df.dropna(subset=["FECHA"])

        df["AÑO"] = df["FECHA"].dt.year
        df["MES"] = df["FECHA"].dt.month_name()

    # MÉTRICAS
    if all(col in df.columns for col in ["VENTAS_CANTIDAD", "PRECIO_VENTA", "COSTOS_VENTA"]):
        df["VENTAS"] = df["VENTAS_CANTIDAD"] * df["PRECIO_VENTA"]
        df["COSTOS"] = df["VENTAS_CANTIDAD"] * df["COSTOS_VENTA"]
        df["GANANCIA"] = df["VENTAS"] - df["COSTOS"]
# =========================
# CREAR MÉTRICAS (ADAPTADO)
# =========================

# 👉 VENTAS (usa cantidad directamente)
    if "VENTAS_CANTIDAD" in df.columns:
        df["VENTAS"] = df["VENTAS_CANTIDAD"]
    
    # 👉 GANANCIA (simulada si no hay costos)
    df["GANANCIA"] = df["VENTAS"] * 0.3  # margen 30% (puedes cambiar)
    
    # 👉 PERIODO
    if "FECHA" in df.columns:
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
        df["PERIODO"] = df["FECHA"].dt.to_period("M").astype(str)    
        
    # PERIODO
    if "FECHA" in df.columns:
        df["PERIODO"] = df["FECHA"].dt.to_period("M").astype(str)

    # 👇 👇 👇 ESTO FALTABA
    df_filtrado = df.copy()
with st.sidebar:

    # =========================
    # 🎨 ESTILO VISUAL
    # =========================
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f4e63, #2c6e8f);
        padding: 15px;
    }

    section[data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 600;
    }

    .stSelectbox > div {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🎯 Filtros")
    st.divider()

    # =========================
    # LIMPIAR ESTADO
    # =========================
    for k in [
        "filtro_pais",
        "filtro_region",
        "filtro_producto",
        "filtro_canal",
        "filtro_vendedor",
        "filtro_tipo_cliente",
        "filtro_fecha"
    ]:
        if isinstance(st.session_state.get(k), list):
            st.session_state[k] = "Todos"

    if "archivo" in st.session_state:

        df_temp = pd.read_excel(st.session_state.archivo)
        df_temp.columns = df_temp.columns.str.strip().str.upper()

        # =========================
        # 🌍 PAIS
        # =========================
        col_pais = next((c for c in df_temp.columns if "PAIS" in c), None)

        if col_pais:
            opciones = ["Todos"] + sorted(df_temp[col_pais].dropna().astype(str).unique())
            pais = st.selectbox("🌍 País", opciones, key="filtro_pais")

            if pais != "Todos":
                df_temp = df_temp[df_temp[col_pais].astype(str) == pais]

        # =========================
        # 📍 REGION
        # =========================
        if "REGION" in df_temp.columns:
            opciones = ["Todos"] + sorted(df_temp["REGION"].dropna().astype(str).unique())
            region = st.selectbox("📍 Región", opciones, key="filtro_region")

            if region != "Todos":
                df_temp = df_temp[df_temp["REGION"].astype(str) == region]

        # =========================
        # 📦 PRODUCTO
        # =========================
        col_producto = next((c for c in df_temp.columns if "PRODUCT" in c), None)

        if col_producto:
            opciones = ["Todos"] + sorted(df_temp[col_producto].dropna().astype(str).unique())
            producto = st.selectbox("📦 Producto", opciones, key="filtro_producto")

            if producto != "Todos":
                df_temp = df_temp[df_temp[col_producto].astype(str) == producto]

        # =========================
        # 📡 CANAL
        # =========================
        if "CANAL" in df_temp.columns:
            opciones = ["Todos"] + sorted(df_temp["CANAL"].dropna().astype(str).unique())
            canal = st.selectbox("📡 Canal", opciones, key="filtro_canal")

            if canal != "Todos":
                df_temp = df_temp[df_temp["CANAL"].astype(str) == canal]

        # =========================
        # 👤 VENDEDOR
        # =========================
        if "VENDEDOR_RUTA" in df_temp.columns:
            opciones = ["Todos"] + sorted(df_temp["VENDEDOR_RUTA"].dropna().astype(str).unique())
            vendedor = st.selectbox("👤 Vendedor", opciones, key="filtro_vendedor")

            if vendedor != "Todos":
                df_temp = df_temp[df_temp["VENDEDOR_RUTA"].astype(str) == vendedor]

        # =========================
        # 🧑‍💼 TIPO CLIENTE
        # =========================
        if "TIPO_CLIENTE" in df_temp.columns:
            opciones = ["Todos"] + sorted(df_temp["TIPO_CLIENTE"].dropna().astype(str).unique())
            tipo = st.selectbox("🧑‍💼 Tipo cliente", opciones, key="filtro_tipo_cliente")

            if tipo != "Todos":
                df_temp = df_temp[df_temp["TIPO_CLIENTE"].astype(str) == tipo]

        # =========================
        # 📅 RANGO DE FECHAS (FIX)
        # =========================
        st.markdown("### 📅 Rango de fechas")

        if "FECHA" in df_temp.columns:

            df_temp["FECHA"] = pd.to_datetime(df_temp["FECHA"], errors="coerce")
            df_temp = df_temp.dropna(subset=["FECHA"])

            fecha_min = df_temp["FECHA"].min()
            fecha_max = df_temp["FECHA"].max()

            fechas = st.date_input(
                "Selecciona rango",
                value=(fecha_min, fecha_max),
                key="filtro_fecha"
            )

            if isinstance(fechas, tuple) and len(fechas) == 2:

                fecha_ini, fecha_fin = fechas

                df_temp = df_temp[
                    (df_temp["FECHA"] >= pd.to_datetime(fecha_ini)) &
                    (df_temp["FECHA"] <= pd.to_datetime(fecha_fin))
                ]

        else:
            st.warning("⚠️ No existe columna FECHA")

        # =========================
        # 🔄 LIMPIAR
        # =========================
        st.divider()
        if st.button("🔄 Limpiar filtros"):
            for k in st.session_state.keys():
                if "filtro_" in k:
                    st.session_state[k] = "Todos"
            st.rerun()

        # =========================
        # 💾 GUARDAR FINAL
        # =========================
        st.session_state["df_filtrado"] = df_temp

    else:
        st.info("📂 Carga un archivo en Inicio")
# ------------------------
# VALIDAR QUE EXISTE df
# ------------------------
if 'df' not in locals() or df is None:
    st.warning("⚠️ No hay archivo cargado o df no existe")
    st.stop()
# =========================
# 1. CARGAR ARCHIVO
# =========================
if "archivo" in st.session_state:
    df = pd.read_excel(st.session_state.archivo)
else:
    st.warning("⚠️ Carga un archivo")
    st.stop()

# =========================
# 2. NORMALIZAR COLUMNAS
# =========================
df.columns = df.columns.str.strip()
df.columns = df.columns.str.upper()

# =========================
# 3. 👉 AQUÍ VA LA RUTINA DE FECHA 👈
# =========================
col_fecha = next((c for c in df.columns if "FECHA" in c), None)

if col_fecha:

    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
    df = df.dropna(subset=[col_fecha])

    if not df.empty:

        fecha_ini, fecha_fin = st.date_input(
            "📅 Selecciona fecha inicial y final",
            value=(df[col_fecha].min(), df[col_fecha].max())
        )

        if fecha_ini and fecha_fin:

            df = df[
                (df[col_fecha] >= pd.to_datetime(fecha_ini)) &
                (df[col_fecha] <= pd.to_datetime(fecha_fin))
            ]

            df["PERIODO"] = df[col_fecha].dt.to_period("M").astype(str)

# =========================
# 4. DESPUÉS VIENE TODO
# =========================
# KPIs
# gráficos
# tablas

# =========================
# SIDEBAR (SOLO NAVEGACIÓN)
# =========================
st.markdown("### 🚦 Navegación")
with st.sidebar:

    st.markdown('<div class="sidebar-title">📊 Analytics Pro</div>', unsafe_allow_html=True)

    if st.button("📊 Principal"):
        st.session_state.vista = "principal"
        st.rerun()

    if st.button("🚦 Volatilidad"):
        st.session_state.vista = "volatilidad"
        st.rerun()

    if st.button("👤 Responsables"):
        st.session_state.vista = "responsables"
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.button("🧠 Causas"):
        st.session_state.vista = "causas"
        st.rerun()

    if st.button("📋 Log"):
        st.session_state.vista = "log"
        st.rerun()

    if st.button("🔍 Detalle"):
        st.session_state.vista = "detalle"
        st.rerun()

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    if st.button("📌 Recomendaciones"):
        st.session_state.vista = "recomendaciones"
        st.rerun() 
               
    if st.button("🧠 Resumen"):
        st.session_state.vista = "resumen"
        st.rerun()
# =========================
# VALIDAR DATA
# =========================
    if df is None:
       st.warning("⚠️ Carga un archivo en Inicio")
       st.stop()


# =========================
# FILTRO DE FECHA (MAIN)
# =========================
if "FECHA" in df.columns:

    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")
    df = df.dropna(subset=["FECHA"])

    if not df.empty:

        #fechas = st.date_input(
        #    "📅 Selecciona fecha inicial y final",
        #    value=(df["FECHA"].min(), df["FECHA"].max())
        #)

        if fecha_ini and fecha_fin:

            df = df[
                (df["FECHA"] >= pd.to_datetime(fecha_ini)) &
                (df["FECHA"] <= pd.to_datetime(fecha_fin))
            ]

            df["PERIODO"] = df["FECHA"].dt.to_period("M").astype(str)

            st.caption(f"📅 Periodo seleccionado: {fecha_ini} → {fecha_fin}")
            st.divider()
        else:
            st.warning("⚠️ Selecciona ambas fechas")

    else:
        st.warning("⚠️ No hay datos válidos en FECHA")

else:
    st.warning("⚠️ El archivo no tiene columna FECHA")



# ------------------------
# PANTALLA INICIAL
# ------------------------

if st.session_state.vista == "inicio":

    st.markdown("## 👈 Selecciona opciones en el panel izquierdo")
    st.image("imagen8.png", width=1400)
    st.write("DEBUG VISTA:", st.session_state.vista)
    st.stop()    

#recomendaciones
# =========================
# RECOMENDACIONES (FINAL FUNCIONAL CORREGIDO)
# =========================
if st.session_state.vista == "recomendaciones":

    if st.button("⬅️ Volver Recomendaciones"):
        st.session_state.vista = "inicio"
        st.rerun()

    st.title("📌 Recomendaciones Estratégicas")

    # ------------------------
    # NORMALIZAR COLUMNAS (CLAVE)
    # ------------------------
    df.columns = df.columns.str.strip().str.upper()

    # ------------------------
    # VALIDACIÓN
    # ------------------------
    if df.empty:
        st.warning("No hay datos con esos filtros")
        st.stop()

    # ------------------------
    # ASEGURAR COLUMNAS
    # ------------------------
    if all(col in df.columns for col in ["VENTAS_CANTIDAD", "PRECIO_VENTA", "COSTOS_VENTA"]):

        df["VENTAS"] = df["VENTAS_CANTIDAD"] * df["PRECIO_VENTA"]
        df["COSTOS"] = df["VENTAS_CANTIDAD"] * df["COSTOS_VENTA"]
        df["GANANCIA"] = df["VENTAS"] - df["COSTOS"]

        if "PERIODO" not in df.columns:
            if "FECHA" in df.columns:
                df["PERIODO"] = pd.to_datetime(df["FECHA"], errors="coerce")\
                    .dt.to_period("M").astype(str)
            else:
                st.error("❌ Falta FECHA o PERIODO")
                st.stop()
    else:
        st.error("❌ El archivo no tiene columnas necesarias")
        st.stop()

    # ------------------------
    # VALIDAR COLUMNAS CLAVE
    # ------------------------
    if not all(col in df.columns for col in ["VENTAS", "PERIODO"]):
        st.error("❌ Faltan columnas necesarias")
        st.stop()

    # ------------------------
    # INICIALIZAR
    # ------------------------
    recomendaciones = []
    resumen_dim = {}

    # ------------------------
    # FUNCIÓN GENERADORA
    # ------------------------
    def generar(df, col):
        df_t = df.groupby(["PERIODO", col])["VENTAS"].sum().reset_index()
        df_t = df_t.sort_values("PERIODO")

        detalle_crece = []
        detalle_cae = []

        for k, g in df_t.groupby(col):
            if g["PERIODO"].nunique() >= 2 and g.iloc[-2]["VENTAS"] != 0:

                v1 = g.iloc[-2]["VENTAS"]
                v2 = g.iloc[-1]["VENTAS"]
                var = (v2 - v1) / v1
                impacto = v2 - v1

                p1 = g.iloc[-2]["PERIODO"]
                p2 = g.iloc[-1]["PERIODO"]

                # 👇 CAMBIO IMPORTANTE: 1% en lugar de 10%
                if abs(var) > 0.01:
                    tipo = "verde" if var > 0 else "rojo"
                    recomendaciones.append((col, k, var, impacto, tipo, v1, v2, p1, p2))

                    if var > 0:
                        detalle_crece.append((k, var))
                    else:
                        detalle_cae.append((k, var))

        return detalle_crece, detalle_cae

    # ------------------------
    # GENERAR
    # ------------------------
    for dim in ["PAIS", "REGION", "CANAL", "NOMBRE_PRODUCTO"]:
        if dim in df.columns:
            crece, cae = generar(df, dim)
            resumen_dim[dim] = {"crece": crece, "cae": cae}

    # ------------------------
    # ORDENAR
    # ------------------------
    if recomendaciones:
        recomendaciones = sorted(recomendaciones, key=lambda x: abs(x[3]), reverse=True)

    st.write("DEBUG recomendaciones:", len(recomendaciones))

    # =========================
    # MOSTRAR
    # =========================
    import plotly.graph_objects as go

    if not recomendaciones:
        st.info("No hay recomendaciones relevantes (>1%)")

    else:
        for r in recomendaciones:

            dim, nombre, var, impacto, tipo, v1, v2, p1, p2 = r

            # TEXTO
            if tipo == "verde":
                st.success(f"🟢 Escalar {dim}: {nombre} ({var:.1%})")
            else:
                st.error(f"🔴 Recuperar {dim}: {nombre} ({var:.1%})")

            st.markdown(f"""
- Periodo anterior ({p1}): ${v1:,.0f}  
- Periodo actual ({p2}): ${v2:,.0f}  
- Variación: {var:.1%}  
- Impacto: ${impacto:,.0f}
""")

            # ------------------------
            # DATA BASE
            # ------------------------
            df_det = df[df[dim].astype(str).str.strip() == str(nombre).strip()]

            # =========================
            # 🔍 DETALLE (CON BULLETS)
            # =========================
            with st.expander(f"🔍 Ver detalle - {nombre}"):

                if df_det.empty:
                    st.warning("No hay datos para este elemento")

                else:
                    tabla = []

                    for subdim in ["NOMBRE_PRODUCTO", "REGION", "CANAL"]:

                        if subdim in df_det.columns and subdim != dim:

                            df_sub = df_det.groupby(["PERIODO", subdim])["VENTAS"].sum().reset_index()

                            for k2, g2 in df_sub.groupby(subdim):

                                if len(g2) >= 2 and g2.iloc[-2]["VENTAS"] != 0:

                                    a1 = g2.iloc[-2]["VENTAS"]
                                    a2 = g2.iloc[-1]["VENTAS"]
                                    var2 = (a2 - a1) / a1

                                    bullet = "🟢" if var2 > 0 else "🔴"

                                    tabla.append([bullet, k2, a1, a2, var2])

                    if tabla:
                        df_detalle = pd.DataFrame(
                            tabla,
                            columns=["", "Elemento", "Anterior", "Actual", "Variación"]
                        )
                        st.dataframe(df_detalle, use_container_width=True)

            # =========================
            # 📊 GRÁFICA (CON SOMBRAS)
            # =========================
            with st.expander(f"📊 Gráfica - {nombre}"):

                if not df_det.empty:

                    df_g = df_det.groupby("PERIODO")["VENTAS"].sum().reset_index()

                    if not df_g.empty:

                        df_g["PERIODO_DT"] = pd.to_datetime(df_g["PERIODO"], errors="coerce")
                        df_g = df_g.sort_values("PERIODO_DT")

                        fig = go.Figure()

                        # SOMBRAS
                        df_g["AÑO"] = df_g["PERIODO_DT"].dt.year
                        for i, año in enumerate(df_g["AÑO"].unique()):
                            df_y = df_g[df_g["AÑO"] == año]

                            fig.add_vrect(
                                x0=df_y["PERIODO_DT"].iloc[0],
                                x1=df_y["PERIODO_DT"].iloc[-1],
                                fillcolor="lightblue" if i % 2 == 0 else "lightgrey",
                                opacity=0.15,
                                line_width=0
                            )

                        fig.add_trace(go.Scatter(
                            x=df_g["PERIODO_DT"],
                            y=df_g["VENTAS"],
                            mode="lines+markers+text",
                            text=[f"${v:,.0f}" for v in df_g["VENTAS"]],
                            textposition="top center"
                        ))

                        st.plotly_chart(fig, use_container_width=True)

                    else:
                        st.warning("Datos vacíos")

                else:
                    st.warning("Sin datos")

            st.markdown("---")
# =========================
# DASHBOARD PRINCIPAL
# =========================
vista = st.session_state.get("vista", "principal")

if vista == "principal":

    st.markdown("## 📊 Dashboard Ejecutivo")

    # =========================
    # CONTEXTO
    # =========================
    st.markdown("### 🎯 Contexto actual")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**🌎 País**")
        st.success(st.session_state.get("filtro_pais", "Todos"))

    with c2:
        st.markdown("**📍 Región**")
        st.success(st.session_state.get("filtro_region", "Todos"))

    with c3:
        st.markdown("**📦 Producto**")
        st.success(st.session_state.get("filtro_producto", "Todos"))

    # =========================
    # DATA BASE
    # =========================
    df_f = st.session_state.get("df_filtrado", df)

    pais = st.session_state.get("filtro_pais", "Todos")
    canal = st.session_state.get("filtro_canal", "Todos")
    region = st.session_state.get("filtro_region", "Todos")

    # =========================
    # FILTROS
    # =========================
    if pais != "Todos" and "PAIS" in df_f.columns:
        df_f = df_f[df_f["PAIS"] == pais]

    if canal != "Todos" and "CANAL" in df_f.columns:
        df_f = df_f[df_f["CANAL"] == canal]

    if region != "Todos" and "REGION" in df_f.columns:
        df_f = df_f[df_f["REGION"] == region]

    # =========================
    # VALIDACIÓN
    # =========================
    if df_f.empty:
        st.warning("⚠️ No hay datos con esos filtros")
        st.stop()

    # =========================
    # FECHA + PERIODO
    # =========================
    col_fecha = next((c for c in df_f.columns if "FECHA" in c), None)

    if not col_fecha:
        st.error("❌ No se encontró columna FECHA")
        st.stop()

    df_f[col_fecha] = pd.to_datetime(df_f[col_fecha], errors="coerce")
    df_f = df_f.dropna(subset=[col_fecha])
    df_f["PERIODO"] = df_f[col_fecha].dt.to_period("M").astype(str)

    # =========================
    # MÉTRICAS
    # =========================
    df_f["VENTAS"] = df_f["VENTAS_CANTIDAD"] * df_f["PRECIO_VENTA"]
    df_f["COSTOS"] = df_f["VENTAS_CANTIDAD"] * df_f["COSTOS_VENTA"]
    df_f["GANANCIA"] = df_f["VENTAS"] - df_f["COSTOS"]

    ventas = df_f["VENTAS"].sum()
    ganancia = df_f["GANANCIA"].sum()
    margen = (ganancia / ventas * 100) if ventas != 0 else 0

    # =========================
    # AGRUPACIÓN
    # =========================
    df_m = df_f.groupby("PERIODO")[["VENTAS", "GANANCIA"]].sum().reset_index()

    # =========================
    # VARIACIÓN
    # =========================
    if len(df_m) >= 2:
        v1 = df_m.iloc[-2]["VENTAS"]
        v2 = df_m.iloc[-1]["VENTAS"]
        variacion = (v2 - v1) / v1 if v1 != 0 else 0
    else:
        variacion = 0

    delta_color = "normal" if variacion >= 0 else "inverse"

    # =========================
    # KPIs
    # =========================
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("💰 Ventas", f"${ventas:,.0f}", f"{variacion:.1%}", delta_color=delta_color)
    k2.metric("📈 Crecimiento", f"{variacion:.1%}")
    k3.metric("💵 Ganancia", f"${ganancia:,.0f}")
    k4.metric("📊 Margen", f"{margen:.1f}%")

    # =========================
    # DEBUG (opcional)
    # =========================
    # st.write("Columnas:", df_f.columns)
    # st.dataframe(df_f.head())

    # =========================
    # ALERTAS
    # =========================
    if margen < 0:
        st.error("🚨 Margen negativo: revisar costos")

    if variacion < 0:
        st.warning("⚠️ Caída en ventas vs periodo anterior")

    # =========================
    # GRÁFICA
    # =========================
    import plotly.graph_objects as go

    fig = go.Figure()

    df_m["PERIODO_DT"] = pd.to_datetime(df_m["PERIODO"], errors="coerce")
    df_m["AÑO"] = df_m["PERIODO_DT"].dt.year

    años = df_m["AÑO"].dropna().unique()

    for j, año in enumerate(años):
        df_year = df_m[df_m["AÑO"] == año]

        if not df_year.empty:
            fig.add_vrect(
                x0=df_year["PERIODO"].iloc[0],
                x1=df_year["PERIODO"].iloc[-1],
                fillcolor="lightblue" if j % 2 == 0 else "lightgrey",
                opacity=0.15,
                line_width=0,
            )

            fig.add_vline(
                x=df_year["PERIODO"].iloc[0],
                line_dash="dash"
            )

    fig.add_trace(go.Scatter(
        x=df_m["PERIODO"],
        y=df_m["VENTAS"],
        mode="lines+markers",
        name="Ventas"
    ))

    fig.add_trace(go.Scatter(
        x=df_m["PERIODO"],
        y=df_m["GANANCIA"],
        mode="lines+markers",
        name="Ganancia"
    ))

    fig.update_layout(
        title="📈 Evolución del negocio",
        xaxis_title="Periodo",
        yaxis_title="Valor",
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # TOP CANAL
    # =========================
    st.markdown("### 🔝 Canal con mayor impacto")

    if not df_f.empty and "CANAL" in df_f.columns:
        top_canal = df_f.groupby("CANAL")["VENTAS"].sum().sort_values(ascending=False).head(1)

        for canal_top, val in top_canal.items():
            st.success(f"🏆 {canal_top} lidera con ${val:,.0f}")

# VOLATILIDAD
elif vista == "volatilidad":

    if st.button("⬅️ Volver principal"):
        st.session_state.vista = "principal"

    st.markdown("## 🚦 Volatilidad")

    ratio = ganancia / ventas if ventas != 0 else 0

    if ratio > 0.3:
        st.error(f"Alta volatilidad ({ratio:.2f})")
    elif ratio > 0.15:
        st.warning(f"Volatilidad media ({ratio:.2f})")
    else:
        st.success(f"Volatilidad baja ({ratio:.2f})")

# RESPONSABLES
elif vista == "responsables":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "inicio"

    st.markdown("## 👤 Responsables")

    if "Vendedor_Ruta" in df.columns:
        df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index()
        st.dataframe(df_r)

# CAUSAS
elif vista == "causas":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "inicio"

    st.markdown("## 🧠 Causas")

    if "Producto" in df.columns:
        df_c = df.groupby("Producto")["Ventas"].sum().reset_index()
        st.dataframe(df_c)

# DETALLE
elif vista == "detalle":

    if st.button("⬅️ Volver"):

        
        st.session_state.vista = "inicio"

    st.markdown("## 🔎 Detalle")
# =========================
# APLICAR FILTROS (CORREGIDO)
# =========================
df_f = st.session_state.get("df_filtrado", df)

if pais != "Todos":
    df_f = df_f[df_f["PAIS"].astype(str) == pais]

if canal != "Todos":
    df_f = df_f[df_f["CANAL"].astype(str) == canal]

if producto and "Todos" not in producto:
    df_f = df_f[df_f["NOMBRE_PRODUCTO"].astype(str) == producto]

if "REGION" in df_f.columns:
    if isinstance(region, list):
        if region:
            df_f = df_f[df_f["REGION"].astype(str).isin(region)]
    else:
        if region != "Todos":
            df_f = df_f[df_f["REGION"].astype(str) == region]
   
# ------------------------
# VALIDACIÓN
# ------------------------
if df_f.empty:
    st.warning("⚠️ No hay datos con esos filtros")
    st.stop()

# ------------------------
# RECÁLCULO
# ------------------------
# =========================
# VALIDACIÓN
# =========================
st.write("COLUMNAS df_f:", df_f.columns.tolist())
st.write("SHAPE df_f:", df_f.shape)
st.stop()
if df_f.empty:
    st.warning("⚠️ No hay datos con esos filtros")
    st.stop()

# =========================
# CÁLCULOS
# =========================
df_f["VENTAS"] = df_f["VENTAS_CANTIDAD"] * df_f["PRECIO_VENTA"]
df_f["COSTOS"] = df_f["VENTAS_CANTIDAD"] * df_f["COSTOS_VENTA"]
df_f["GANANCIA"] = df_f["VENTAS"] - df_f["COSTOS"]

# =========================
# GROUPBY SEGURO
# =========================
if all(col in df_f.columns for col in ["PERIODO", "VENTAS", "GANANCIA"]):
    df_m = df_f.groupby("PERIODO")[["VENTAS", "GANANCIA"]].sum().reset_index()
else:
    df_m = pd.DataFrame()
    st.warning("⚠️ Faltan columnas para cálculo (PERIODO, VENTAS, GANANCIA)")

# =========================
# KPIs
# =========================
ventas = df_f["VENTAS"].sum() if "VENTAS" in df_f.columns else 0
ganancia = df_f["GANANCIA"].sum() if "GANANCIA" in df_f.columns else 0
margen = (ganancia / ventas * 100) if ventas != 0 else 0


# ------------------------
# DASHBOARD PRINCIPAL
# ------------------------

vista = st.session_state.vista

if vista == "principal":
    st.markdown("## 📊 Dashboard Ejecutivo")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas", f"${ventas:,.0f}")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    if not df_m.empty:
        fig = px.line(df_m, x="PERIODO", y=["VENTAS", "GANANCIA"], markers=True)
        st.plotly_chart(fig, use_container_width=True, key="grafica_3")
    else:
        st.warning("No hay datos para graficar")

elif vista == "volatilidad":

    if st.button("⬅️ Volver Ejecutivo"):
        st.session_state.vista = "principal"

    st.markdown("## 🚦 Volatilidad")

    ratio = ganancia / ventas if ventas != 0 else 0

    if ratio > 0.3:
        st.error(f"Alta volatilidad ({ratio:.2f})")
    elif ratio > 0.15:
        st.warning(f"Volatilidad media ({ratio:.2f})")
    else:
        st.success(f"Volatilidad baja ({ratio:.2f})")

elif vista == "responsables":

    if st.button("⬅️ Volver Responsable"):
        st.session_state.vista = "principal"

    st.markdown("## 👤 Responsables")

    if "Vendedor_Ruta" in df.columns:
        df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index()
        st.dataframe(df_r)

elif vista == "causas":

    if st.button("⬅️ Volver Causa"):
        st.session_state.vista = "principal"

    st.markdown("## 🧠 Causas")

    if "Producto" in df.columns:
        df_c = df.groupby("Producto")["Ventas"].sum().reset_index()
        st.dataframe(df_c)

# 🔥 NUEVAS VISTAS CONECTADAS

elif vista == "reporte":

    if st.button("⬅️ Volver Reporte"):
        st.session_state.vista = "principal"

    st.markdown("## 📊 Reporte Ejecutivo")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas", f"${ventas:,.0f}")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    if not df_m.empty:
        fig = px.bar(df_m, x="Periodo", y="Ventas")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos para graficar")

elif vista == "log":

    if st.button("⬅️ Volver Log"):
        st.session_state.vista = "principal"

    st.markdown("## 📋 Log")

    st.write("Filas cargadas:", len(df))
    st.dataframe(df.head(20))

elif vista == "recomendaciones":
    
    if st.button("⬅️ Volver Recomendacion"):
        st.session_state.vista = "inicio"

    st.markdown("## 📌 Recomendacioneszzzz")

    if margen < 20:
        st.error("Margen bajo: revisar costos o precios")
    elif margen < 35:
        st.warning("Margen medio: optimizar operación")
    else:
        st.success("Margen saludable: escalar negocio")

#### alertas 
elif st.session_state.vista == "alertas":

    st.title("🚨 Dashboard de Alertas")

    if st.button("⬅️ Volver a Resumen"):
        st.session_state.vista = "resumen"
        st.rerun()

    df_res = df.copy()
    tabla = []
    
    # =========================
    # GENERAR BASE
    # =========================
    for dim in ["Canal", "Pais", "Region", "Producto"]:
        if dim in df_res.columns:
            continue    
        if "Periodo" not in df_res.columns or "Ventas" not in df_res.columns:
            continue    
            df_t = df_res.groupby(["Periodo", dim])["Ventas"].sum().reset_index()
            df_t["Periodo"] = pd.to_datetime(df_t["Periodo"])
            df_t = df_t.sort_values("Periodo")
##################################################################################################
            for k, g in df_t.groupby(dim):

                if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:

                    v1 = g.iloc[-2]["Ventas"]
                    v2 = g.iloc[-1]["Ventas"]

                    var = (v2 - v1) / v1
                    impacto = (v2 - v1)

                    tabla.append([dim, k, v1, v2, var, impacto])

    df_alertas = pd.DataFrame(
        tabla,
        columns=["Dimensión", "Elemento", "Anterior", "Actual", "Variación", "Impacto $"]
    )

    if not df_alertas.empty:

        df_alertas = df_alertas[abs(df_alertas["Variación"]) > 0.3]

        st.markdown("## 🚨 Alertas detectadas")

        for i, row in df_alertas.iterrows():

            dim = row["Dimensión"]
            nombre = row["Elemento"]
            var = row["Variación"]

            st.warning(f"...")
            df_det = df[df[dim] == nombre]

            # =========================
            # DETALLE TABLA
            # =========================
            with st.expander(f"🔍 Ver detalle - {nombre}"):

                tabla_det = []

                for subdim in ["Producto", "    Region", "Canal"]:
                    if subdim in df_det.columns and subdim != dim:

                        df_sub = df_det.groupby(["Periodo", subdim])["Ventas"].sum().reset_index()
                        df_sub = df_sub.sort_values("Periodo")

                        for k2, g2 in df_sub.groupby(subdim):

                            if len(g2) >= 2 and g2.iloc[-2]["Ventas"] != 0:

                                v1_sub = g2.iloc[-2]["Ventas"]
                                v2_sub = g2.iloc[-1]["Ventas"]
                                var_sub = (v2_sub - v1_sub) / v1_sub

                                semaforo = "🟢" if var_sub > 0 else "🔴"

                                tabla_det.append([
                                    subdim,
                                    k2,
                                    v1_sub,
                                    v2_sub,
                                    f"{semaforo} {var_sub:.1%}"
                                ])

                if tabla_det:
                    df_tabla_det = pd.DataFrame(
                        tabla_det,
                        columns=["Dimensión", "Elemento", "Anterior", "Actual", "Variación"]
                    )
                    st.dataframe(df_tabla_det.head(5), use_container_width=True)

            # =========================
            # GRÁFICA (ARREGLADA)
            # =========================
            with st.expander(f"📊 Ver gráfica - {nombre}"):

                import plotly.graph_objects as go

                df_g = df_det.groupby("Periodo")["Ventas"].sum().reset_index()
                df_g["Periodo_dt"] = pd.to_datetime(df_g["Periodo"])
                df_g = df_g.sort_values("Periodo_dt")

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=df_g["Periodo"],
                    y=df_g["Ventas"],
                    mode="lines+markers+text",
                    text=[f"${v:,.0f}" for v in df_g["Ventas"]],
                    textposition="top center"
                ))

                fig.update_layout(
                    title=f"{nombre} | Variación {var:.1%}",
                    xaxis_title="Periodo",
                    yaxis_title="Ventas",
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True, key=f"alert_{i}")

            st.markdown("---")

        # =========================
        # TABLA GENERAL
        # =========================
        st.markdown("### 📋 Tabla completa")

        df_display = df_alertas.copy()
        df_display["Variación"] = df_display["Variación"].apply(
            lambda x: f"🔴 {x:.1%}" if x < 0 else f"🟢 {x:.1%}"
        )
        df_display["Impacto $"] = df_display["Impacto $"].apply(
            lambda x: f"🔴 ${x:,.0f}" if x < 0 else f"🟢 ${x:,.0f}"
        )

        st.dataframe(df_display, use_container_width=True)

    else:
        st.info("No hay alertas relevantes")

    st.stop()
# =======================
# RESUMEN EJECUTIVO PRO
# =======================
st.write("👉 VISTA ACTUAL:", st.session_state.get("vista"))
if st.session_state.get("vista") == "resumen":
    st.write("✅ ENTRÉ AL RESUMEN")
if st.session_state.vista == "resumen":
    st.write("Vista actual:", st.session_state.get("vista"))
    st.title("🧠 Resumen Ejecutivo")
    # =========================
    # DATA BASE (USA FILTROS)
    # =========================
    df_res = st.session_state.get("df_filtrado", df)

    if df_res is None or df_res.empty:
        st.error("❌ No hay datos disponibles")
        st.stop()

    df_res = df_res.copy()
    df_res.columns = df_res.columns.str.strip().str.upper()

    # =========================
    # FECHA → PERIODO
    # =========================
    col_fecha = next((c for c in df_res.columns if "FECHA" in c), None)

    if not col_fecha:
        st.error("❌ No existe columna FECHA")
        st.write(df_res.columns)
        st.stop()

    df_res[col_fecha] = pd.to_datetime(df_res[col_fecha], errors="coerce")
    df_res = df_res.dropna(subset=[col_fecha])

    if df_res.empty:
        st.error("❌ No hay fechas válidas")
        st.stop()

    df_res["PERIODO"] = df_res[col_fecha].dt.to_period("M").astype(str)

    # =========================
    # MÉTRICAS
    # =========================
    if "VENTAS" not in df_res.columns:
        if all(c in df_res.columns for c in ["VENTAS_CANTIDAD", "PRECIO_VENTA"]):
            df_res["VENTAS"] = df_res["VENTAS_CANTIDAD"] * df_res["PRECIO_VENTA"]
        else:
            st.error("❌ Faltan columnas para calcular VENTAS")
            st.stop()

    if "COSTOS" not in df_res.columns and "COSTOS_VENTA" in df_res.columns:
        df_res["COSTOS"] = df_res["VENTAS_CANTIDAD"] * df_res["COSTOS_VENTA"]

    if "GANANCIA" not in df_res.columns and "COSTOS" in df_res.columns:
        df_res["GANANCIA"] = df_res["VENTAS"] - df_res["COSTOS"]

    # =========================
    # AGRUPACIÓN
    # =========================
    df_m = df_res.groupby("PERIODO")[["VENTAS", "GANANCIA"]].sum().reset_index()

    if df_m.empty:
        st.warning("⚠️ No hay datos para mostrar")
        st.stop()

    df_m = df_m.sort_values("PERIODO")

# =========================
# FIX DATA RESUMEN (OBLIGATORIO)
# =========================

    df_f = st.session_state.get("df_filtrado", df).copy()
    df_f.columns = df_f.columns.str.strip().str.upper()
    
    # 👉 FECHA → PERIODO
    if "FECHA" in df_f.columns:
        df_f["FECHA"] = pd.to_datetime(df_f["FECHA"], errors="coerce")
        df_f = df_f.dropna(subset=["FECHA"])
        df_f["PERIODO"] = df_f["FECHA"].dt.to_period("M").astype(str)
    else:
        st.error("❌ No existe columna FECHA")
        st.stop()
    
    # 👉 VENTAS (SI NO EXISTE PRECIO)
    if "VENTAS" not in df_f.columns:
        if "VENTAS_CANTIDAD" in df_f.columns:
            df_f["VENTAS"] = df_f["VENTAS_CANTIDAD"]
        else:
            st.error("❌ No existe columna VENTAS_CANTIDAD")
            st.stop()
    
    # 👉 COSTOS (SIMULADO SI NO EXISTE)
    if "COSTOS" not in df_f.columns:
        df_f["COSTOS"] = df_f["VENTAS"] * 0.7  # ajustable
    
    # 👉 GANANCIA
    df_f["GANANCIA"] = df_f["VENTAS"] - df_f["COSTOS"]
    
    # DEBUG
    st.write("✅ COLUMNAS FINALES:", df_f.columns)
    st.write("📊 SHAPE:", df_f.shape)
    # =========================
    # KPIs EJECUTIVOS
    # =========================
    ventas = df_res["VENTAS"].sum()
    ganancia = df_res["GANANCIA"].sum() if "GANANCIA" in df_res.columns else 0
    margen = (ganancia / ventas * 100) if ventas != 0 else 0

    variacion = 0
    if len(df_m) >= 2:
        v1 = df_m.iloc[-2]["VENTAS"]
        v2 = df_m.iloc[-1]["VENTAS"]
        if v1 != 0:
            variacion = (v2 - v1) / v1

    delta_color = "normal" if variacion >= 0 else "inverse"

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("💰 Ventas", f"${ventas:,.0f}", f"{variacion:.1%}", delta_color=delta_color)
    k2.metric("📈 Crecimiento", f"{variacion:.1%}")
    k3.metric("💵 Ganancia", f"${ganancia:,.0f}")
    k4.metric("📊 Margen", f"{margen:.1f}%")

    st.divider()

    # =========================
    # GRÁFICA PRINCIPAL
    # =========================
    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_m["PERIODO"],
        y=df_m["VENTAS"],
        mode="lines+markers",
        name="Ventas"
    ))

    if "GANANCIA" in df_m.columns:
        fig.add_trace(go.Scatter(
            x=df_m["PERIODO"],
            y=df_m["GANANCIA"],
            mode="lines+markers",
            name="Ganancia"
        ))

    fig.update_layout(
        title="📈 Evolución del negocio",
        xaxis_title="Periodo",
        yaxis_title="Valor",
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # PROYECCIÓN SIMPLE
    # =========================
    st.subheader("🔮 Proyección")

    if len(df_m) >= 2:
        tendencia = df_m["VENTAS"].diff().mean()
        proyeccion = df_m["VENTAS"].iloc[-1] + tendencia

        st.info(f"📊 Proyección próximo periodo: ${proyeccion:,.0f}")

    # =========================
    # TOP DIMENSIÓN
    # =========================
    st.subheader("🏆 Mayor contribución")

    for dim in ["CANAL", "PAIS", "REGION", "PRODUCTO", "NOMBRE_PRODUCTO"]:
        if dim in df_res.columns:

            top = df_res.groupby(dim)["VENTAS"].sum().sort_values(ascending=False).head(1)

            if not top.empty:
                for k, v in top.items():
                    st.success(f"🔥 {dim}: {k} → ${v:,.0f}")
                break

    # =========================
    # ALERTAS
    # =========================
    st.subheader("🚨 Alertas")

    if margen < 0:
        st.error("Margen negativo")

    if variacion < 0:
        st.warning("Caída en ventas vs periodo anterior")

    if variacion > 0.2:
        st.success("Alto crecimiento detectado")

    # =========================
    # TABLA FINAL
    # =========================
    st.subheader("📋 Detalle")

    st.dataframe(df_res.head(100), use_container_width=True)
# =========================
# LOG
# =========================
if st.session_state.vista == "log":

    if st.button("⬅️ Volver log"):
        st.session_state.vista = "principal"
        st.rerun()

    st.title("📋 Log de Carga")

    log = st.session_state.get("log_carga")

    if log:
        col1, col2, col3 = st.columns(3)

        col1.metric("Filas originales", log.get("original", 0))
        col2.metric("Filas cargadas", log.get("final", 0))
        col3.metric("Filas eliminadas", log.get("eliminadas", 0))

        st.markdown("### 🧹 Registros eliminados")

        if not log.get("df_eliminadas", pd.DataFrame()).empty:
            st.dataframe(log["df_eliminadas"])

            csv = log["df_eliminadas"].to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Descargar errores en Excel",
                data=csv,
                file_name="errores_carga.csv",
                mime="text/csv"
            )
        else:
            st.success("No hubo errores en la carga")
