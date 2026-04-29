import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard BI", layout="wide")

st.markdown("""
<style>
.kpi-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}
.kpi-title {
    font-size: 14px;
    color: #9CA3AF;
}
.kpi-value {
    font-size: 28px;
    font-weight: bold;
}
.kpi-card:hover {
    transform: scale(1.05);
    transition: 0.3s;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
</style>
""", unsafe_allow_html=True)
st.title("📊 Dashboard de Ventas")

# -------------------------
# version nueva 
# -------------------------

st.markdown("### 📊 Análisis de Ventas y Rentabilidad")
st.caption("Dashboard interactivo para análisis comercial")
st.markdown("---")

# -------------------------
# Cargar archivo
# -------------------------
archivo = st.file_uploader("📁 Sube tu Excel", type=["xlsx", "csv"])

if archivo is None:
    st.stop()

# -------------------------
# Leer datos
# -------------------------
@st.cache_data
def cargar_datos(archivo):
    if archivo.name.endswith(".csv"):
        return pd.read_csv(archivo)
    else:
        return pd.read_excel(archivo)

df = cargar_datos(archivo)

# 🔥 limpiar columnas (evita errores)
df.columns = df.columns.str.strip()

# 🔥 optimización
df = df.head(300)

# -------------------------
# FILTROS
# -------------------------
st.sidebar.header("🎛️ Filtros")

# Cliente
if "Nombre" in df.columns:
    nombres = st.sidebar.multiselect(
        "👤 Cliente", df["Nombre"].dropna().unique()
    )
    if nombres:
        df = df[df["Nombre"].isin(nombres)]

# Producto
if "Producto" in df.columns:
    productos = st.sidebar.multiselect(
        "📦 Producto", df["Producto"].dropna().unique()
    )
    if productos:
        df = df[df["Producto"].isin(productos)]

# -------------------------
# PROCESAMIENTO
# -------------------------
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

tipo = st.sidebar.selectbox("📅 Agrupar por", ["Día", "Mes", "Año"])

if tipo == "Día":
    df["Periodo"] = df["Fecha"]
elif tipo == "Mes":
    df["Periodo"] = df["Fecha"].dt.to_period("M").dt.to_timestamp()
else:
    df["Periodo"] = df["Fecha"].dt.to_period("Y").dt.to_timestamp()

df_group = df.groupby("Periodo")[["Ventas", "Costos"]].sum().reset_index()
df_group = df_group.sort_values("Periodo")

# -------------------------
# CÁLCULOS
# -------------------------
df_group["Ganancia"] = df_group["Ventas"] - df_group["Costos"]
df_group["Margen %"] = (df_group["Ganancia"] / df_group["Ventas"]) * 100
df_group["Crecimiento %"] = df_group["Ventas"].pct_change() * 100

# -------------------------
# KPIs
# -------------------------
# -------------------------
# KPIs CAMBIOS VERSION 2
# -------------------------

st.markdown("""
<style>
.kpi-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}
.kpi-title {
    font-size: 14px;
    color: #9CA3AF;
}
.kpi-value {
    font-size: 28px;
    font-weight: bold;
}
.kpi-card:hover {
    transform: scale(1.05);
    transition: 0.3s;
}
#</style>
#""", unsafe_allow_html=True)
#kpi-title {
#    font-size: 14px;
#    color: #9CA3AF;
#}
#.kpi-value {
#    font-size: 28px;
#    font-weight: bold;
#}
</style>
""", unsafe_allow_html=True)
st.markdown("---")

st.subheader("📊 KPIs")

#col1, col2, col3, col4 = st.columns(4)

#col1.metric("💰 Ventas", round(df_group["Ventas"].sum(), 2))
#col2.metric("💸 Costos", round(df_group["Costos"].sum(), 2))
#col3.metric("📈 Ganancia", round(df_group["Ganancia"].sum(), 2))
#col4.metric("📊 Margen %", round(df_group["Margen %"].mean(), 2))
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Ventas</div>
<div class="kpi-value">{round(ventas_total,2)}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Costos</div>
<div class="kpi-value">{round(costos_total,2)}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card">
<div class="kpi-title">Ganancia</div>
<div class="kpi-value">{round(ganancia_total,2)}</div>
</div>
""", unsafe_allow_html=True)

#col4.markdown(f"""
#<div class="kpi-card">
#<div class="kpi-title">Margen %</div>
#<div class="kpi-value">{round(margen,2)}%</div>
#</div>
#""", unsafe_allow_html=True)

# -------------------------
# nuevos cambios
# -------------------------

st.markdown("---")

# KPI con delta
if len(df_group) > 1:
    delta = df_group["Ventas"].iloc[-1] - df_group["Ventas"].iloc[-2]

    st.metric(
        "Ventas actuales",
        round(df_group["Ventas"].iloc[-1], 2),
        delta=round(delta, 2)
    )
# -------------------------
# nuevos cambios INSIGHT
# -------------------------
st.markdown("---")
st.subheader("🧠 Insights automáticos")

st.markdown("---")
st.subheader("📈 Análisis Visual")

col1, col2 = st.columns(2)

with col1:
    st.write("Tendencia")
    st.line_chart(df_group.set_index("Periodo")[["Ventas", "Ganancia"]])

with col2:
    st.write("Ventas")
    st.bar_chart(df_group.set_index("Periodo")["Ventas"])
# -------------------------
# ALERTA
# -------------------------
if len(df_group) > 1:
    crecimiento = df_group["Crecimiento %"].iloc[-1]

    if crecimiento > 0:
        st.success(f"📈 Crecimiento: {round(crecimiento,2)}%")
    else:
        st.error(f"📉 Caída: {round(crecimiento,2)}%")

# -------------------------
# GRÁFICAS
# -------------------------
# -------------------------
# cambios nuevos
# -------------------------

st.markdown("---")
st.subheader("📈 Análisis Visual")

col1, col2 = st.columns(2)

with col1:
    st.write("Tendencia")
    st.line_chart(df_group.set_index("Periodo")[["Ventas", "Ganancia"]])

with col2:
    st.write("Ventas")
    st.bar_chart(df_group.set_index("Periodo")["Ventas"])

#st.subheader("📈 Tendencia")
#st.line_chart(
#    df_group.set_index("Periodo")[["Ventas", "Costos", "Ganancia"]]
#)

#st.subheader("📊 Ventas por periodo")
#st.bar_chart(df_group.set_index("Periodo")["Ventas"])

# -------------------------
# VENTAS POR PRODUCTO
# -------------------------
if "Producto" in df.columns:
    st.subheader("📦 Ventas por Producto")

    ventas_prod = (
        df.groupby("Producto")["Ventas"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(ventas_prod)

# -------------------------
# VENTAS POR CLIENTE
# -------------------------
if "Nombre" in df.columns:
    st.subheader("👤 Ventas por Cliente")

    ventas_cliente = (
        df.groupby("Nombre")["Ventas"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    st.bar_chart(ventas_cliente)

# -------------------------
# TOP CLIENTES
# -------------------------
if "Nombre" in df.columns:
    st.subheader("🏆 Top Clientes")

    top_clientes = (
        df.groupby("Nombre")["Ventas"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    st.dataframe(top_clientes)

# -------------------------
# DATOS
# -------------------------
with st.expander("📂 Ver datos completos"):
    st.dataframe(df_group)

# -------------------------
# DESCARGA
# -------------------------
csv = df_group.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Descargar resultados",
    csv,
    "dashboard_resultados.csv",
    "text/csv"
)
