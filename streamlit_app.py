import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard PRO", layout="wide")

st.title("📊 Dashboard de Ventas PRO")

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

# 🔥 optimización
df = df.head(200)

# -------------------------
# FILTROS
# -------------------------
st.sidebar.header("🎛️ Filtros")

if "Producto" in df.columns:
    productos = st.sidebar.multiselect(
        "Producto", df["Producto"].dropna().unique()
    )
    if productos:
        df = df[df["Producto"].isin(productos)]

if "Región" in df.columns:
    regiones = st.sidebar.multiselect(
        "Región", df["Región"].dropna().unique()
    )
    if regiones:
        df = df[df["Región"].isin(regiones)]

# -------------------------
# Procesar
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
# Cálculos
# -------------------------
df_group["Ganancia"] = df_group["Ventas"] - df_group["Costos"]
df_group["Margen %"] = (df_group["Ganancia"] / df_group["Ventas"]) * 100
df_group["Crecimiento %"] = df_group["Ventas"].pct_change() * 100

# -------------------------
# KPIs
# -------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Ventas", round(df_group["Ventas"].sum(), 2))
col2.metric("💸 Costos", round(df_group["Costos"].sum(), 2))
col3.metric("📈 Ganancia", round(df_group["Ganancia"].sum(), 2))
col4.metric("📊 Margen %", round(df_group["Margen %"].mean(), 2))

# -------------------------
# ALERTA DE CRECIMIENTO
# -------------------------
if len(df_group) > 1:
    crecimiento = df_group["Crecimiento %"].iloc[-1]

    if crecimiento > 0:
        st.success(f"📈 Crecimiento: {round(crecimiento,2)}%")
    else:
        st.error(f"📉 Caída: {round(crecimiento,2)}%")

# -------------------------
# COMPARACIÓN
# -------------------------
if len(df_group) > 1:
    actual = df_group["Ventas"].iloc[-1]
    anterior = df_group["Ventas"].iloc[-2]

    st.write(f"Ventas actuales: {round(actual,2)}")
    st.write(f"Ventas periodo anterior: {round(anterior,2)}")

# -------------------------
# GRÁFICA PRINCIPAL
# -------------------------
st.subheader("📈 Tendencia")

st.line_chart(
    df_group.set_index("Periodo")[["Ventas", "Ganancia"]]
)

# -------------------------
# TOP PRODUCTOS
# -------------------------
if "Producto" in df.columns:
    st.subheader("🏆 Top 5 Productos")

    top = (
        df.groupby("Producto")["Ventas"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    st.dataframe(top)

# -------------------------
# TABLA
# -------------------------
st.subheader("📊 Datos")
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
