import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import streamlit_authenticator as stauth

# ------------------------
# CONFIG
# ------------------------
st.markdown("""
<style>
/* Fondo gris para egación */
.-container {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# ------------------------
#  SIEMPRE ARRIBA
# ------------------------
st.image("LOOGO-TIDS-CONSULTING (2).jpg", width=150)
st.markdown("### TIDS CONSULTING")
# ------------------------
# LOGIN
# ------------------------
from streamlit_authenticator import Hasher
import streamlit_authenticator as stauth

passwords = ["1234", "abcd"]
hashed_passwords = Hasher(passwords).generate()

names = ["Admin", "Ventas"]
usernames = ["admin", "ventas"]

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

name, authentication_status, username = authenticator.login("Login", location="main")
# ------------------------
# CONTROL LOGIN (CLAVE)
# ------------------------
if authentication_status is False:
    st.error("Usuario o contraseña incorrectos")
    st.stop()

elif authentication_status is None:
    st.warning("Ingresa tus credenciales")
    st.stop()

# ------------------------
# LOGIN OK
# ------------------------
st.sidebar.write(f"👋 Bienvenido {name}")
authenticator.logout("Cerrar sesión", "sidebar")

# ------------------------
# SESSION STATE
# ------------------------
if "vista" not in st.session_state:
    st.session_state.vista = "principal"

# ------------------------
# BASE DE DATOS
# ------------------------
conn = sqlite3.connect("data.db")

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

# ------------------------
# CARGA ARCHIVO
# ------------------------
archivo = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if not archivo:
    st.info("📂 Sube un archivo para comenzar")
    st.stop()

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
# FILTROS + NAV (FIX)
# ------------------------
df_base = df.copy()

with st.sidebar:

    st.divider()
    st.markdown("### 🎯 Filtros")

    df = df_base.copy()

    # PAÍS
    if "Pais" in df.columns:
        pais = st.multiselect(
            "País",
            sorted(df["Pais"].dropna().unique()),
            default=sorted(df["Pais"].dropna().unique()),
            key="pais"
        )
        df = df[df["Pais"].isin(pais)]

    # REGIÓN
    if "Region" in df.columns:
        region = st.multiselect(
            "Región",
            sorted(df["Region"].dropna().unique()),
            default=sorted(df["Region"].dropna().unique()),
            key="region"
        )
        df = df[df["Region"].isin(region)]

    # PERIODO
    st.markdown("### 📅 Periodo")

    periodos = sorted(df["Periodo"].dropna().unique())

    if periodos:
        periodo_sel = st.multiselect(
            "Periodo",
            periodos,
            default=periodos[-2:] if len(periodos) >= 2 else periodos,
            key="periodo"
        )
        df = df[df["Periodo"].isin(periodo_sel)]

    st.divider()

    # NAVEGACIÓN
    st.markdown("### 🚦 Navegación")

    if st.button("📊 Principal"):
        st.session_state.vista = "principal"

    if st.button("🚦 Volatilidad"):
        st.session_state.vista = "volatilidad"

    if st.button("👤 Responsables"):
        st.session_state.vista = "responsables"

    if st.button("🧠 Causas"):
        st.session_state.vista = "causas"

    if st.button("📋 Log"):
        st.session_state.vista = "log"

    if st.button("🔎 Detalle"):
        st.session_state.vista = "detalle"

    if st.button("📌 Recomendaciones"):
        st.session_state.vista = "recomendaciones"

    if st.button("🧠 Resumen"):
        st.session_state.vista = "resumen"

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
# DASHBOARD
# ------------------------
vista = st.session_state.vista

# PRINCIPAL
if vista == "principal":

    st.markdown("## 📊 Dashboard Ejecutivo")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas", f"${ventas:,.0f}")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

# VOLATILIDAD
elif vista == "volatilidad":

    if st.button("⬅️ Volver"):
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
        st.session_state.vista = "principal"

    st.markdown("## 👤 Responsables")

    if "Vendedor_Ruta" in df.columns:
        df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index()
        st.dataframe(df_r)

# CAUSAS
elif vista == "causas":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.markdown("## 🧠 Causas")

    if "Producto" in df.columns:
        df_c = df.groupby("Producto")["Ventas"].sum().reset_index()
        st.dataframe(df_c)

# DETALLE
elif vista == "detalle":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.markdown("## 🔎 Detalle")
    st.dataframe(df)

# 🔥 DATA FINAL FILTRADA
df = df_f.copy()
# 🔥 ESTE ES EL DF FINAL QUE USA TODO
df = df_f.copy()

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
# DASHBOARD
# ------------------------
vista = st.session_state.vista

if vista == "principal":
    st.markdown("## 📊 Dashboard Ejecutivo")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas", f"${ventas:,.0f}")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    fig = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

elif vista == "volatilidad":

    if st.button("⬅️ Volver"):
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

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.markdown("## 👤 Responsables")

    if "Vendedor_Ruta" in df.columns:
        df_r = df.groupby("Vendedor_Ruta")["Ventas"].sum().reset_index()
        st.dataframe(df_r)

elif vista == "causas":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.markdown("## 🧠 Causas")

    if "Producto" in df.columns:
        df_c = df.groupby("Producto")["Ventas"].sum().reset_index()
        st.dataframe(df_c)

# 🔥 NUEVAS VISTAS CONECTADAS

elif vista == "reporte":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.markdown("## 📊 Reporte Ejecutivo")

    c1, c2, c3 = st.columns(3)
    c1.metric("Ventas", f"${ventas:,.0f}")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    fig = px.bar(df_m, x="Periodo", y="Ventas")
    st.plotly_chart(fig, use_container_width=True)

elif vista == "log":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.markdown("## 📋 Log")

    st.write("Filas cargadas:", len(df))
    st.dataframe(df.head(20))

elif vista == "recomendaciones":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.markdown("## 📌 Recomendaciones")

    if margen < 20:
        st.error("Margen bajo: revisar costos o precios")
    elif margen < 35:
        st.warning("Margen medio: optimizar operación")
    else:
        st.success("Margen saludable: escalar negocio")
# =======================
# RESUMEN
# =======================
elif st.session_state.vista == "resumen":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.title("🧠 Resumen Ejecutivo")
    st.subheader("📈 Proyección")

    if len(df_m) > 2:
        tendencia = df_m["Ventas"].diff().mean()
        df_m["Proyección"] = df_m["Ventas"].iloc[-1] + tendencia

        fig = px.line(df_m, x="Periodo", y=["Ventas", "Proyección"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

    def color_valores(val):
        try:
            val = float(val)
            if val < 0:
                return 'color: red'
            elif val > 0:
                return 'color: green'
        except:
            return ''
        return ''

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

                    estado = "Crece" if var > 0 else "Cae"

                    tabla.append([dim, k, v1, v2, var, impacto, estado])

    df_tabla = pd.DataFrame(
        tabla,
        columns=["Dimensión", "Elemento", "Anterior", "Actual", "Variación", "Impacto $", "Estado"]
    )

    if not df_tabla.empty:
        df_display = df_tabla.copy()
        df_display["Variación"] = df_display["Variación"].apply(lambda x: format_color(x, "var"))
        df_display["Impacto $"] = df_display["Impacto $"].apply(lambda x: format_color(x, "money"))

        st.dataframe(df_display)

# =========================
# RECOMENDACIONES (INTACTO)
# =========================
elif st.session_state.vista == "recomendaciones":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.title("📌 Recomendaciones Estratégicas")

    recomendaciones = []

    def generar(df, col):
        df_t = df.groupby(["Periodo", col])["Ventas"].sum().reset_index()
        df_t = df_t.sort_values("Periodo")

        detalle_crece = []
        detalle_cae = []

        for k, g in df_t.groupby(col):
            if len(g) >= 2 and g.iloc[-2]["Ventas"] != 0:

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

    resumen_dim = {}

    for dim in ["Pais", "Region", "Canal", "Producto"]:
        if dim in df.columns:
            crece, cae = generar(df, dim)
            resumen_dim[dim] = {"crece": crece, "cae": cae}

    recomendaciones = sorted(recomendaciones, key=lambda x: x[3], reverse=True)

    for dim, nombre, var, impacto, tipo, v1, v2, p1, p2 in recomendaciones:

        if tipo == "verde":
            st.success(f"🟢 Escalar {dim}: {nombre} ({var*100:.1f}%)")
        else:
            st.error(f"🔴 Recuperar {dim}: {nombre} ({var*100:.1f}%)")

        st.markdown(f"""
        - Periodo anterior ({p1}): ${v1:,.0f}  
        - Periodo actual ({p2}): ${v2:,.0f}  
        - Variación: (({v2:,.0f} - {v1:,.0f}) / {v1:,.0f}) = **{var*100:.1f}%**
        """)

        df_det = df[df[dim] == nombre]

        for subdim in ["Producto", "Region", "Canal"]:
            if subdim in df_det.columns and subdim != dim:
                top = df_det.groupby(subdim)["Ventas"].sum().reset_index().sort_values("Ventas", ascending=False).head(1)
                if not top.empty:
                    st.info(f"Driver principal: {subdim} → {top.iloc[0][subdim]} (${top.iloc[0]['Ventas']:,.0f})")
                    break

        with st.expander("🔍 Ver detalle"):

            for subdim in ["Producto", "Region", "Canal"]:
                if subdim in df_det.columns and subdim != dim:

                    df_sub = df_det.groupby(["Periodo", subdim])["Ventas"].sum().reset_index()
                    df_sub = df_sub.sort_values("Periodo")

                    tabla = []

                    for k2, g2 in df_sub.groupby(subdim):

                        if len(g2) >= 2 and g2.iloc[-2]["Ventas"] != 0:

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

        with st.expander("📊 Ver gráfica"):

            df_f = df[df[dim] == nombre]
            df_g = df_f.groupby("Periodo")["Ventas"].sum().reset_index()

            if len(df_g) >= 2:

                df_g["Periodo_dt"] = pd.to_datetime(df_g["Periodo"])
                df_g = df_g.sort_values("Periodo_dt")

                v1 = df_g.iloc[-2]["Ventas"]
                v2 = df_g.iloc[-1]["Ventas"]

                if v1 != 0:
                    var_g = (v2 - v1) / v1
                    proy = v2 * (1 + var_g)

                    sig = df_g["Periodo_dt"].iloc[-1] + pd.DateOffset(months=1)

                    df_g = pd.concat([
                        df_g,
                        pd.DataFrame({
                            "Periodo": [sig.strftime("%Y-%m")],
                            "Ventas": [proy]
                        })
                    ])

            fig = px.line(df_g, x="Periodo", y="Ventas", markers=True)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
# =========================
# DETALLE
# =========================
elif st.session_state.vista == "detalle":

    if st.button("⬅️ Volver"):
        st.session_state.vista = "principal"

    st.title("🔎 Análisis Detallado")
    st.dataframe(df)

# =========================
# LOG
# =========================
elif st.session_state.vista == "log":

    if st.button("⬅️ Volver"):
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
            st.success("No hubo registros eliminados")    
