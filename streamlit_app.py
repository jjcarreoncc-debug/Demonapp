import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import streamlit_authenticator as stauth
from streamlit_authenticator import Hasher
import hashlib
from datetime import datetime
from PIL import Image

# ------------------------
# CONFIG
# ------------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# ------------------------
# BASE DE DATOS
# ------------------------
conn = sqlite3.connect("data.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS ventas (
    Fecha TEXT,
    Nombre_Producto TEXT,
    Numero_Producto TEXT,
    Ventas_Cantidad REAL,
    Pais TEXT,
    Region TEXT,
    Canal TEXT,
    Vendedor_Ruta TEXT,
    Tipo_cliente TEXT,
    Precio_Venta REAL,
    Costos_Venta REAL
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    nombre TEXT,
    rol TEXT,
    estado TEXT,
    fecha_creacion TEXT
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
if authentication_status is False:
    st.error("Usuario o contraseña incorrectos")
    st.stop()

if authentication_status is None:
    col1, col2 = st.columns([2,6])
    with col2:
        img = Image.open("imagen7.png")
        st.image(img, width=2000)
    st.stop()

# ------------------------
# SIDEBAR + MENÚ
# ------------------------
st.sidebar.title("📌 Navegación")
st.sidebar.write(f"👋 Bienvenido {name}")
authenticator.logout("Cerrar sesión", "sidebar")

rol = "Admin" if username == "admin" else "Usuario"

if rol == "Admin":
    menu = st.sidebar.radio("Menú", ["Dashboard", "Mantenimiento"])
else:
    menu = st.sidebar.radio("Menú", ["Dashboard"])

# ------------------------
# FUNCIONES USUARIOS
# ------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def obtener_usuarios():
    return pd.read_sql("SELECT * FROM usuarios", conn)

def crear_usuario(username, password, nombre, rol):
    try:
        conn.execute("""
        INSERT INTO usuarios (username, password, nombre, rol, estado, fecha_creacion)
        VALUES (?, ?, ?, ?, 'Activo', ?)
        """, (
            username,
            hash_password(password),
            nombre,
            rol,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return True
    except Exception as e:
        return str(e)

def desactivar_usuario(user_id):
    conn.execute("UPDATE usuarios SET estado='Inactivo' WHERE id=?", (user_id,))
    conn.commit()

# ------------------------
# MANTENIMIENTO
# ------------------------
if menu == "Mantenimiento":

    st.header("⚙️ Mantenimiento de Usuarios")

    with st.expander("➕ Crear Usuario"):
        username_new = st.text_input("Usuario nuevo")
        password_new = st.text_input("Contraseña", type="password")
        nombre_new = st.text_input("Nombre")
        rol_new = st.selectbox("Rol", ["Admin", "Usuario"])

        if st.button("Guardar usuario"):
            resultado = crear_usuario(username_new, password_new, nombre_new, rol_new)

            if resultado == True:
                st.success("Usuario creado")
            else:
                st.error(f"Error: {resultado}")

    st.subheader("Usuarios registrados")
    usuarios_df = obtener_usuarios()

    if not usuarios_df.empty:
        st.dataframe(usuarios_df)

        user_id = st.selectbox("Seleccionar usuario ID", usuarios_df["id"])

        if st.button("Desactivar usuario"):
            desactivar_usuario(user_id)
            st.warning("Usuario desactivado")
    else:
        st.info("No hay usuarios aún")

# ------------------------
# DASHBOARD
# ------------------------
if menu == "Dashboard":

    st.header("📊 Dashboard Ejecutivo")

    archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

    if not archivo:
        st.info("📂 Sube un archivo para comenzar")

    else:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()

        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df = df.dropna(subset=["Fecha"])

        for col in ["Ventas_Cantidad", "Precio_Venta", "Costos_Venta"]:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                    .str.replace(",", "")
                    .str.strip()
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df["Ventas"] = df["Ventas_Cantidad"] * df["Precio_Venta"]
        df["Costos"] = df["Ventas_Cantidad"] * df["Costos_Venta"]
        df["Ganancia"] = df["Ventas"] - df["Costos"]
        df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

        # 🔥 YA NO ROMPE
        if 'df' in locals():
            df_base = df.copy()

        col1, col2, col3 = st.columns(3)
        col1.metric("Ventas Totales", f"${df['Ventas'].sum():,.0f}")
        col2.metric("Costos Totales", f"${df['Costos'].sum():,.0f}")
        col3.metric("Ganancia", f"${df['Ganancia'].sum():,.0f}")

        fig = px.bar(df, x="Periodo", y="Ventas", title="Ventas por Periodo")
        st.plotly_chart(fig, use_container_width=True)
# ------------------------
# DASHBOARD MENIU
# ------------------------
# ------------------------
# DASHBOARD
# ------------------------
if menu == "Dashboard":

    # ------------------------
    # CARGA ARCHIVO
    # ------------------------
    archivo = st.file_uploader("Archivo 1", type=["xlsx"], key="file1")
    if not archivo:
        st.info("📂 Sube un archivo para comenzar")

    else:
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip()

        # ------------------------
        # LIMPIEZA
        # ------------------------
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df = df.dropna(subset=["Fecha"])

        for col in ["Ventas_Cantidad", "Precio_Venta", "Costos_Venta"]:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "")
                    .str.strip()
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # ------------------------
        # MÉTRICAS
        # ------------------------
        df["Ventas"] = df["Ventas_Cantidad"] * df["Precio_Venta"]
        df["Costos"] = df["Ventas_Cantidad"] * df["Costos_Venta"]
        df["Ganancia"] = df["Ventas"] - df["Costos"]
        df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

        # ------------------------
        # 🔥 AQUÍ VA TU BLOQUE DE FILTROS
        # ------------------------
        if 'df' in locals():
            df_base = df.copy()

        # (pega aquí TODO tu bloque de filtros)

        # ------------------------
        # GRÁFICOS
        # ------------------------
        st.header("📊 Dashboard Ejecutivo")

        col1, col2, col3 = st.columns(3)
        col1.metric("Ventas Totales", f"${df['Ventas'].sum():,.0f}")
        col2.metric("Costos Totales", f"${df['Costos'].sum():,.0f}")
        col3.metric("Ganancia", f"${df['Ganancia'].sum():,.0f}")
    fig = px.bar(df, x="Periodo", y="Ventas", title="Ventas por Periodo")
    st.plotly_chart(fig, use_container_width=True)
# ------------------------
# FILTROS + NAV (CON PRODUCTO, CANAL, VENDEDOR, TIPO_CLIENTE + RANGO DE FECHAS)
# ------------------------
if 'df' in locals():
    df_base = df.copy()


with st.sidebar:

    st.divider()
    st.markdown("### 🎯 Filtros")
    if 'df' in locals():
        df_base = df.copy()
   # PAÍS
    if "Pais" in df.columns:
        pais = st.multiselect(
            "País",
            sorted(df["Pais"].dropna().unique()),
            default=sorted(df["Pais"].dropna().unique()),
            key="filtro_pais"
        )
        df = df[df["Pais"].isin(pais)]

    # REGIÓN
    if "Region" in df.columns:
        region = st.multiselect(
            "Región",
            sorted(df["Region"].dropna().unique()),
            default=sorted(df["Region"].dropna().unique()),
            key="filtro_region"
        )
        df = df[df["Region"].isin(region)]

    # PRODUCTO
    if "Producto" in df.columns:
        producto = st.multiselect(
            "Producto",
            sorted(df["Producto"].dropna().unique()),
            default=sorted(df["Producto"].dropna().unique()),
            key="filtro_producto"
        )
        df = df[df["Producto"].isin(producto)]

    # CANAL
    if "Canal" in df.columns:
        canal = st.multiselect(
            "Canal",
            sorted(df["Canal"].dropna().unique()),
            default=sorted(df["Canal"].dropna().unique()),
            key="filtro_canal"
        )
        df = df[df["Canal"].isin(canal)]

    # VENDEDOR
    if "Vendedor_Ruta" in df.columns:
        vendedor = st.multiselect(
            "Vendedor",
            sorted(df["Vendedor_Ruta"].dropna().unique()),
            default=sorted(df["Vendedor_Ruta"].dropna().unique()),
            key="filtro_vendedor"
        )
        df = df[df["Vendedor_Ruta"].isin(vendedor)]

    # TIPO CLIENTE
    if "Tipo_cliente" in df.columns:
        tipo_cliente = st.multiselect(
            "Tipo cliente",
            sorted(df["Tipo_cliente"].dropna().unique()),
            default=sorted(df["Tipo_cliente"].dropna().unique()),
            key="filtro_tipo_cliente"
        )
        df = df[df["Tipo_cliente"].isin(tipo_cliente)]

    # ------------------------
    # RANGO DE FECHAS
    # ------------------------
    st.markdown("### 📅 Rango de fechas")
    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    fecha_ini, fecha_fin = st.date_input(
        "Selecciona fecha inicial y final",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
        key="filtro_rango_fecha"
    )

    df = df[(df["Fecha"] >= pd.to_datetime(fecha_ini)) &
            (df["Fecha"] <= pd.to_datetime(fecha_fin))]

    # recalcular Periodo
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    st.caption(f"📅 Periodo seleccionado: {fecha_ini} → {fecha_fin}")
    st.divider()

    # ------------------------
    # NAVEGACIÓN
    # ------------------------
    st.markdown("### 🚦 Navegación")

    if st.button("📊 Principal", key="nav_principal"):
        st.session_state.vista = "principal"

    if st.button("🚦 Volatilidad", key="nav_volatilidad"):
        st.session_state.vista = "volatilidad"

    if st.button("👤 Responsables", key="nav_responsables"):
        st.session_state.vista = "responsables"

    if st.button("🧠 Causas", key="nav_causas"):
        st.session_state.vista = "causas"

    if st.button("📋 Log", key="nav_log"):
        st.session_state.vista = "log"

    if st.button("🔎 Detalle", key="nav_detalle"):
        st.session_state.vista = "detalle"

    if st.button("📌 Recomendaciones", key="nav_recomendaciones"):
        st.session_state.vista = "recomendaciones"

    if st.button("🧠 Resumen", key="nav_resumen"):
        st.session_state.vista = "resumen"
    # ------------------------
# PANTALLA INICIAL
# ------------------------

if st.session_state.get("vista") == "inicio":

    st.markdown("## 👈 Selecciona opciones en el panel izquierdo")
    st.image("imagen8.png", width=1400)

    st.stop()    
# ------------------------
# MINI DASHBOARD DE DEBUG CON VENTAS, COSTOS Y PRECIO
# =========================
# =========================
# RECOMENDACIONES (FINAL REAL)
# =========================
if st.session_state.vista == "recomendaciones":

    if st.button("⬅️ Volver Recomendaciones "):
        
        st.session_state.vista = "inicio"
# ------------------------
# PANTALLA INICIAL (NO TOCAR LO DEMÁS)
# --
 
    
    st.title("📌 Recomendaciones Estratégicas")

    recomendaciones = []

    # Función para generar recomendaciones reales
    def generar(df, col):
        df_t = df.groupby(["Periodo", col])["Ventas"].sum().reset_index()
        df_t = df_t.sort_values("Periodo")

        detalle_crece = []
        detalle_cae = []

        for k, g in df_t.groupby(col):
            if g["Periodo"].nunique() >= 2 and g.iloc[-2]["Ventas"] != 0:
                v1 = g.iloc[-2]["Ventas"]
                v2 = g.iloc[-1]["Ventas"]
                var = (v2 - v1) / v1
                impacto = abs(var * v2)
                p1 = g.iloc[-2]["Periodo"]
                p2 = g.iloc[-1]["Periodo"]

                if var < -0.10:
                    recomendaciones.append((col, k, var, impacto, "rojo", v1, v2, p1, p2))
                    detalle_cae.append((k, var))
                elif var > 0.10:
                    recomendaciones.append((col, k, var, impacto, "verde", v1, v2, p1, p2))
                    detalle_crece.append((k, var))
        return detalle_crece, detalle_cae

    # Generar recomendaciones por dimensión
    resumen_dim = {}
    for dim in ["Pais", "Region", "Canal", "Producto"]:
        if dim in df.columns:
            crece, cae = generar(df, dim)
            resumen_dim[dim] = {"crece": crece, "cae": cae}

    recomendaciones = sorted(recomendaciones, key=lambda x: x[3], reverse=True)

    # Mostrar recomendaciones
    for dim, nombre, var, impacto, tipo, v1, v2, p1, p2 in recomendaciones:
        if tipo == "verde":
            st.success(f"🟢 Escalar {dim}: {nombre} ({var*100:.1f}%)")
        else:
            st.error(f"🔴 Recuperar {dim}: {nombre} ({var*100:.1f}%)")

        st.markdown(f"""
        - Periodo anterior ({p1}): ${v1:,.0f}  
        - Periodo actual ({p2}): ${v2:,.0f}  
        - Variación: {var*100:.1f}%
        """)

        df_det = df[df[dim] == nombre]

        # 🔹 Botón Ver detalle
        with st.expander("🔍 Ver detalle"):
            for subdim in ["Producto", "Region", "Canal"]:
                if subdim in df_det.columns and subdim != dim:
                    df_sub = df_det.groupby(["Periodo", subdim])["Ventas"].sum().reset_index()
                    df_sub = df_sub.sort_values("Periodo")
                    tabla = []
                    for k2, g2 in df_sub.groupby(subdim):
                        if g2["Periodo"].nunique() >= 2 and g2.iloc[-2]["Ventas"] != 0:
                            a1 = g2.iloc[-2]["Ventas"]
                            a2 = g2.iloc[-1]["Ventas"]
                            var2 = (a2 - a1) / a1
                            tabla.append([k2, a1, a2, var2])
                    if tabla:
                        df_detalle = pd.DataFrame(tabla, columns=["Elemento", "Anterior", "Actual", "Variación"])
                        df_detalle["Variación"] = df_detalle["Variación"].apply(
                            lambda x: f"🔴 {x:.1%}" if x < 0 else f"🟢 {x:.1%}"
                        )
                        st.dataframe(df_detalle.head(5))

        # 🔹 Botón Ver gráfica
        with st.expander("📊 Ver gráfica"):
            df_g = df_det.groupby("Periodo")["Ventas"].sum().reset_index()
            df_g["Periodo_dt"] = pd.to_datetime(df_g["Periodo"].astype(str))
            df_g = df_g.sort_values("Periodo_dt")

            if len(df_g) >= 2:
                v1_g = df_g.iloc[-2]["Ventas"]
                v2_g = df_g.iloc[-1]["Ventas"]
                var_g = (v2_g - v1_g) / v1_g if v1_g != 0 else 0
                proy = v2_g * (1 + var_g)
                sig = df_g["Periodo_dt"].iloc[-1] + pd.DateOffset(months=1)
                df_g = pd.concat([
                    df_g,
                    pd.DataFrame({
                        "Periodo": [sig.strftime("%Y-%m")],
                        "Ventas": [proy]
                    })
                ])

            fig = px.line(df_g, x="Periodo", y="Ventas", markers=True)
            st.plotly_chart(fig, use_container_width=True, key=f"graf_{dim}_{nombre}")

        st.markdown("---")
# ------------------------
# VALIDACIÓN
# ------------------------
if df.empty:
    st.warning("No hay datos con esos filtros")
    st.stop()

# ------------------------
# RECÁLCULO
# ------------------------
df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()

ventas = df["Ventas"].sum()
ganancia = df["Ganancia"].sum()
margen = (ganancia / ventas * 100) if ventas != 0 else 0

# ------------------------
# DASHBOARD PRINCIPAL
# ------------------------vista = st.session_state.vista
vista = st.session_state.vista
if vista == "principal":

    st.markdown("## 📊 Dashboard Ejecutivo")

    # =========================
    # FILTROS (si ya los tienes arriba, puedes omitir)
    # =========================
    df_f = df.copy()
    
    
    if pais and "Todos" not in pais:
        df_f = df_f[df_f["Pais"].isin(pais)]

    if canal and "Todos" not in canal:
        df_f = df_f[df_f["Canal"].isin(canal)]

    if region and "Todos" not in region:
        df_f = df_f[df_f["Region"].isin(region)]
    producto = st.multiselect(
    "Producto",
    ["Todos"] + sorted(df["Nombre_Producto"].dropna().unique()),
    default=["Todos"],
    key="principal_producto"
)
    if producto and "Todos" not in producto: 
        
        df_f = df_f[df_f["Producto"].isin(producto)]
    # =========================
    # CALCULOS BASE (CENTRALIZADO)
    # =========================
    df_f["Ventas"] = df_f["Ventas_Cantidad"] * df_f["Precio_Venta"]
    df_f["Costos"] = df_f["Ventas_Cantidad"] * df_f["Costos_Venta"]
    df_f["Ganancia"] = df_f["Ventas"] - df_f["Costos"]

    ventas = df_f["Ventas"].sum()
    costos = df_f["Costos"].sum()
    ganancia = df_f["Ganancia"].sum()
    margen = (ganancia / ventas) * 100 if ventas != 0 else 0

    # =========================
    # DATA MENSUAL
    # =========================
    df_m = df_f.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()
    df_m = df_m.sort_values("Periodo")

    # =========================
    # VARIACIÓN
    # =========================
    if len(df_m) >= 2:
        v1 = df_m.iloc[-2]["Ventas"]
        v2 = df_m.iloc[-1]["Ventas"]
        var = (v2 - v1) / v1 if v1 != 0 else 0
    else:
        var = 0

    # =========================
    # KPIs PRO
    # =========================
    c1, c2, c3 = st.columns(3)

    c1.metric("Ventas", f"${ventas:,.0f}", f"{var:.1%}")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    # =========================
    # ALERTAS AUTOMÁTICAS
    # =========================
    if margen < 0:
        st.error("🚨 Margen negativo: revisar costos")

    if var < 0:
        st.warning("⚠️ Caída en ventas vs periodo anterior")

    # =========================
    # GRÁFICA PRO
    # =========================
    import plotly.graph_objects as go

    fig = go.Figure()

    # SOMBRAS POR AÑO
    df_m["Periodo_dt"] = pd.to_datetime(df_m["Periodo"])
    df_m["Año"] = df_m["Periodo_dt"].dt.year
    años = df_m["Año"].unique()

    for j, año in enumerate(años):
        df_year = df_m[df_m["Año"] == año]

        fig.add_vrect(
            x0=df_year["Periodo"].iloc[0],
            x1=df_year["Periodo"].iloc[-1],
            fillcolor="lightblue" if j % 2 == 0 else "lightgrey",
            opacity=0.15,
            line_width=0,
        )

        fig.add_vline(
            x=df_year["Periodo"].iloc[0],
            line_dash="dash"
        )

    # LINEAS
    fig.add_trace(go.Scatter(
        x=df_m["Periodo"],
        y=df_m["Ventas"],
        mode="lines+markers",
        name="Ventas"
    ))

    fig.add_trace(go.Scatter(
        x=df_m["Periodo"],
        y=df_m["Ganancia"],
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

    if not df_f.empty:
        top_canal = df_f.groupby("Canal")["Ventas"].sum().sort_values(ascending=False).head(1)

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

    if st.button("⬅️ Volver responsables "):
        st.sesion_state.vista = "inicio"

    st.markdown("## 👤 Responsables")

    if "Vendedor_Ruta" in df.columns:
        df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index()
        st.dataframe(df_r)

# CAUSAS
elif vista == "causas":

    if st.button("⬅️ Volver Causa "):
        st.session_state.vista = "inicio"

    st.markdown("## 🧠 Causas")

    if "Producto" in df.columns:
        df_c = df.groupby("Producto")["Ventas"].sum().reset_index()
        st.dataframe(df_c)

# DETALLE
elif vista == "detalle":

    if st.button("⬅️ Volver detalle"):

        st.st.session_state.vista = "inicio":

    st.markdown("## 🔎 Detalle")
    # =========================
# FILTROS EN DETALLE
# =========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    pais = st.selectbox(
        "País",
        ["Todos"] + sorted(df["Pais"].dropna().unique()),
        key="detalle_pais"
    )

with col2:
    canal = st.selectbox(
        "Canal",
        ["Todos"] + sorted(df["Canal"].dropna().unique()),
        key="detalle_canal"
    )

with col3:
    region = st.selectbox(
        "Región",
        ["Todos"] + sorted(df["Region"].dropna().unique()),
        key="detalle_region"
    )

with col4:
    producto = st.selectbox(
        "Producto",
        ["Todos"] + sorted(df["Nombre_Producto"].dropna().unique()),
        key="detalle_producto"
    )


# =========================
# APLICAR FILTROS
# =========================
df_f = df.copy()

if pais != "Todos":
    df_f = df_f[df_f["Pais"] == pais]

if canal != "Todos":
    df_f = df_f[df_f["Canal"] == canal]

if producto != "Todos":
    df_f = df_f[df_f["Nombre_Producto"] == producto]
    st.dataframe(df)
if "Region" in df_f.columns:
    if isinstance(region, list):
        if region:
            df_f = df_f[df_f["Region"].isin(region)]
    else:
        if region != "Todos":
            df_f = df_f[df_f["Region"] == region]
      

# 🔥 DATA FINAL FILTRADA

# 🔥 ESTE ES EL DF FINAL QUE USA TODO


# ------------------------
# VALIDACIÓN
# ------------------------
if df.empty:
    st.warning("No hay datos con esos filtros")
    st.stop()

# ------------------------
# RECÁLCULO
# ------------------------
df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()

ventas = df["Ventas"].sum()
ganancia = df["Ganancia"].sum()
margen = (ganancia / ventas * 100) if ventas != 0 else 0

# ------------------------
# DASHBOARD PRINCIAPL
# ------------------------
vista = st.session_state.vista

if vista == "principal":
    st.markdown("## 📊 Dashboard Ejecutivo")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas", f"${ventas:,.0f}")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
    st.plotly_chart(fig, use_container_width=True, key="grafica_3")

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

    fig = px.bar(df_m, x="Periodo", y="Ventas")
    st.plotly_chart(fig, use_container_width=True)

elif vista == "log":

    if st.button("⬅️ Volver Log"):
        st.session_state.vista = "principal"

    st.markdown("## 📋 Log")

    st.write("Filas cargadas:", len(df))
    st.dataframe(df.head(20))

elif vista == "recomendaciones":

    if st.button("⬅️ Volver Recomendacion"):
        st.session_state.vista = "principal"

    st.markdown("## 📌 Recomendaciones")

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

            df_t = df_res.groupby(["Periodo", dim])["Ventas"].sum().reset_index()
            df_t["Periodo"] = pd.to_datetime(df_t["Periodo"])
            df_t = df_t.sort_values("Periodo")

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
# RESUMEN
# =======================
elif st.session_state.vista == "resumen":

    if st.button("⬅️ Volver Resumen"):
        st.st.session_state.get("vista") == "inicio":
        st.rerun()

    st.title("🧠 Resumen Ejecutivo")

    # =========================
    # DATA
    # =========================
    df_m = df.groupby("Periodo")["Ventas"].sum().reset_index()
    df_m = df_m.sort_values("Periodo")

    # =========================
    # PROYECCIÓN
    # =========================
    st.subheader("📈 Proyección")

    if len(df_m) > 2:
        tendencia = df_m["Ventas"].diff().mean()
        df_m["Proyección"] = df_m["Ventas"].iloc[-1] + tendencia

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(df_m, x="Periodo", y="Ventas", markers=True)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(df_m, x="Periodo", y=["Ventas", "Proyección"], markers=True)
            st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # FORMATO
    # =========================
    def format_color(val, tipo):
        try:
            val = float(val)
            if tipo == "var":
                return f"🔴 {val:.2%}" if val < 0 else f"🟢 {val:.2%}"
            elif tipo == "money":
                return f"🔴 ${val:,.0f}" if val < 0 else f"🟢 ${val:,.0f}"
        except:
            return val
        return val

    st.markdown("## 📊 Análisis adicional de desempeño")

    df_res = df.copy()
    tabla = []

    # =========================
    # TABLA BASE
    # =========================
    for dim in ["Canal", "Pais", "Region", "Producto"]:
        if dim in df_res.columns:

            df_t = df_res.groupby(["Periodo", dim])["Ventas"].sum().reset_index()
            df_t["Periodo"] = pd.to_datetime(df_t["Periodo"])
            df_t = df_t.sort_values("Periodo")

            for k, g in df_t.groupby(dim):

                if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:

                    v1 = g.iloc[-2]["Ventas"]
                    v2 = g.iloc[-1]["Ventas"]

                    var = (v2 - v1) / v1
                    impacto = (v2 - v1)

                    estado = "🟢 Crece" if var > 0 else "🔴 Cae"

                    tabla.append([dim, k, v1, v2, var, impacto, estado])

    df_tabla = pd.DataFrame(
        tabla,
        columns=["Dimensión", "Elemento", "Anterior", "Actual", "Variación", "Impacto $", "Estado"]
    )

    # =========================
    # INSIGHTS
    # =========================
    if not df_tabla.empty:

        st.markdown("## 🧠 Insights automáticos")

        top_crece = df_tabla.sort_values("Impacto $", ascending=False).head(1)
        top_cae = df_tabla.sort_values("Impacto $").head(1)

        if not top_crece.empty:
            row = top_crece.iloc[0]
            st.success(f"🔥 Crecimiento impulsado por {row['Elemento']} (${row['Impacto $']:,.0f})")

        if not top_cae.empty:
            row = top_cae.iloc[0]
            st.error(f"⚠️ Caída principal en {row['Elemento']} (${row['Impacto $']:,.0f})")

    # =========================
    # BOTÓN ALERTAS (NUEVO)
    # =========================
    st.markdown("---")
    if st.button("🚨 Ver dashboard de alertas"):
        st.session_state.vista = "alertas"
        st.rerun()

    # =========================
    # TOP IMPACTOS
    # =========================
    if not df_tabla.empty:

        st.markdown("### 🔝 Principales impactos")

        top = df_tabla.sort_values("Impacto $", ascending=False).head(5)

        for i, row in top.iterrows():

            dim = row["Dimensión"]
            nombre = row["Elemento"]
            impacto = row["Impacto $"]

            if impacto > 0:
                st.success(f"🟢 {nombre} impulsa (${impacto:,.0f})")
            else:
                st.error(f"🔴 {nombre} afecta (${impacto:,.0f})")

            df_det = df[df[dim] == nombre]

            # =========================
            # DETALLE
            # =========================
            with st.expander(f"🔍 Detalle - {nombre}"):

                df_detalle = df_det.groupby("Periodo")["Ventas"].sum().reset_index()
                st.dataframe(df_detalle)

            # =========================
            # GRÁFICA (ARREGLADA + SOMBRAS)
            # =========================
            with st.expander(f"📊 Gráfica - {nombre}"):

                import plotly.graph_objects as go

                df_g = df_det.groupby("Periodo")["Ventas"].sum().reset_index()
                df_g["Periodo_dt"] = pd.to_datetime(df_g["Periodo"])
                df_g = df_g.sort_values("Periodo_dt")

                if len(df_g) >= 2:
                    v1 = df_g.iloc[-2]["Ventas"]
                    v2 = df_g.iloc[-1]["Ventas"]
                    var = (v2 - v1) / v1 if v1 != 0 else 0
                else:
                    var = 0
                fig = go.Figure()

                    # SOMBRAS
                df_g["Año"] = df_g["Periodo_dt"].dt.year
                años = df_g["Año"].unique()

                for j, año in enumerate(años):
                    df_year = df_g[df_g["Año"] == año]

                    fig.add_vrect(
                        x0=df_year["Periodo"].iloc[0],
                        x1=df_year["Periodo"].iloc[-1],
                        fillcolor="lightblue" if j % 2 == 0 else "lightgrey",
                        
                        opacity=0.2,
                        line_width=0,
                    )

                    fig.add_vline(
                        x=df_year["Periodo"].iloc[0],
                        line_dash="dash"
                    )

                fig.add_trace(go.Scatter(
                    x=df_g["Periodo"],
                    y=df_g["Ventas"],
                    mode="lines+markers+text",
                    text=[f"${v:,.0f}" for v in df_g["Ventas"]],
                    textposition="top center"
                ))
                               
                st.plotly_chart(fig, use_container_width=True)               
    st.stop()
# =========================
# DETALLE (LIMPIO Y ESTABLE)
# =========================
elif st.session_state.vista == "detalle":

    # BOTÓN
    if st.button("⬅️ Volver", key="volver_detalle"):
        st.st.session_state.get("vista") == "inicio":
        st.rerun()

    st.title("🔎 Análisis Detallado")

    # =========================
    # FILTROS
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pais = st.selectbox(
            "País",
            ["Todos"] + sorted(df["Pais"].dropna().unique()),
            key="detalle_pais_1"
        )

    with col2:
        canal = st.selectbox(
            "Canal",
            ["Todos"] + sorted(df["Canal"].dropna().unique()),
            key="detalle_canal_1"
        )

    with col3:
        region = st.selectbox(
            "Región",
            ["Todos"] + sorted(df["Region"].dropna().unique()),
            key="detalle_region_1"
        )

    with col4:
        producto = st.selectbox(
            "Producto",
            ["Todos"] + sorted(df["Nombre_Producto"].dropna().unique()),
            key="detalle_producto_1"
        )
# =========================
    # FILTRADO
    # =========================
    df_f = df.copy()

    if canal != "Todos":
        df_f = df_f[df_f["Canal"] == canal]

    if pais != "Todos":
        df_f = df_f[df_f["Pais"] == pais]

    if isinstance(region, list):
        if region:
            df_f = df_f[df_f["Region"].isin(region)]
    else:
        if region != "Todos":
            df_f = df_f[df_f["Region"] == region]

    # =========================
    # DATA PARA GRÁFICA
    # =========================
    df_g = df_f.groupby("Periodo")["Ventas"].sum().reset_index()
    df_g["Periodo_dt"] = pd.to_datetime(df_g["Periodo"])
    df_g = df_g.sort_values("Periodo_dt")

    # =========================
    # KPIs
    # =========================
    col1, col2, col3 = st.columns(3)

    total = df_f["Ventas"].sum()

    if len(df_g) >= 2:
        v1 = df_g.iloc[-2]["Ventas"]
        v2 = df_g.iloc[-1]["Ventas"]
        var = (v2 - v1) / v1 if v1 != 0 else 0
    else:
        var = 0

    with col1:
        st.metric("Ventas totales", f"${total:,.0f}")

    with col2:
        if not df_g.empty:
            st.metric("Último periodo", f"${df_g.iloc[-1]['Ventas']:,.0f}")

    with col3:
        st.metric("Variación", f"{var:.1%}")

    # =========================
    # GRÁFICA CON SOMBRAS
    # =========================
    import plotly.graph_objects as go

    fig = go.Figure()

    if not df_g.empty:

        df_g["Año"] = df_g["Periodo_dt"].dt.year
        años = df_g["Año"].unique()

        for j, año in enumerate(años):
            df_year = df_g[df_g["Año"] == año]

            fig.add_vrect(
                x0=df_year["Periodo_dt"].iloc[0],
                x1=df_year["Periodo_dt"].iloc[-1],
                fillcolor="lightblue" if j % 2 == 0 else "lightgrey",
                opacity=0.2,
                line_width=0,
            )

            fig.add_vline(
                x=df_year["Periodo_dt"].iloc[0],
                line_dash="dash"
            )

        fig.add_trace(go.Scatter(
            x=df_g["Periodo_dt"],
            y=df_g["Ventas"],
            mode="lines+markers+text",
            text=[f"${v:,.0f}" for v in df_g["Ventas"]],
            textposition="top center"
        ))

    fig.update_layout(
        title="Evolución de Ventas",
        xaxis_title="Periodo",
        yaxis_title="Ventas",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # INSIGHT SIMPLE
    # =========================
    st.info(f"Filtro: Canal={canal} | País={pais} | Región={region}")

    if var > 0:
        st.success(f"📈 Crecimiento de {var:.1%}")
    else:
        st.error(f"📉 Caída de {var:.1%}")

    # =========================
    # TOP REGIONES
    # =========================
    st.markdown("### 🔝 Top regiones")

    top = df_f.groupby("Region")["Ventas"].sum().sort_values(ascending=False).head(5)
    st.bar_chart(top)

    # =========================
    # TABLA
    # =========================
    st.markdown("### 📋 Datos")
    st.dataframe(df_f, use_container_width=True)
# =========================
# LOG
# =========================
if st.session_state.vista == "log":

    if st.button("⬅️ Volver log"):
        st.session_state.vista = "principal"
        st.experimental_rerun()

    st.title("📋 Log de Carga")

    log = st.session_state.get("log_carga")

    if log:
        col1, col2, col3 = st.columns(3)

        col1.metric("Filas originales", log["original"])
        col2.metric("Filas cargadas", log["final"])
        col3.metric("Filas eliminadas", log["eliminadas"])

        st.markdown("### 🧹 Registros eliminados")

        if not log["df_eliminadas"].empty:
            st.dataframe(log["df_eliminadas"])

            csv = log["df_eliminadas"].to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Descargar errores en Excel",
                data=csv,
                file_name="errores_carga.csv",
                mime="text/csv"
            )

        else:
            st.s
