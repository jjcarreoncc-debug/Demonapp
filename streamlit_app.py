import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Fechas OK", layout="wide")

st.title("📊 Dashboard por Fecha")

# -------------------------
# Cargar archivo
# -------------------------
archivo = st.file_uploader("📁 Sube tu Excel", type=["xlsx", "csv"])

if archivo is not None:
    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo)
    else:
        df = pd.read_excel(archivo)
else:
    st.warning("⚠️ Sube un archivo")
    st.stop()

# -------------------------
# Validar columnas
# -------------------------
if "Fecha" not in df.columns:
    st.error("❌ Debe existir columna 'Fecha'")
    st.write("Columnas encontradas:", df.columns)
    st.stop()

# -------------------------
# Convertir fecha
# -------------------------
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

# -------------------------
# Asegurar columnas numéricas
# -------------------------
if "Ventas" in df.columns:
    df["Ventas"] = pd.to_numeric(df["Ventas"], errors="coerce")

if "Costos" in df.columns:
    df["Costos"] = pd.to_numeric(df["Costos"], errors="coerce")

# -------------------------
# Sidebar filtros
# -------------------------
col_valores = st.sidebar.multiselect(
    "Selecciona métricas",
    ["Ventas", "Costos"],
    default=["Ventas", "Costos"]
)

if len(col_valores) == 0:
    st.warning("Selecciona al menos una métrica")
    st.stop()

tipo = st.sidebar.selectbox("Agrupar por", ["Día", "Mes", "Año"])

# -------------------------
# Crear Periodo
# -------------------------
if tipo == "Día":
    df["Periodo"] = df["Fecha"]
elif tipo == "Mes":
    df["Periodo"] = df["Fecha"].dt.to_period("M").dt.to_timestamp()
else:
    df["Periodo"] = df["Fecha"].dt.to_period("Y").dt.to_timestamp()

# -------------------------
# Agrupar
# -------------------------
df_group = df.groupby("Periodo")[col_valores].sum().reset_index()
df_group = df_group.sort_values("Periodo")

# -------------------------
# KPI
# -------------------------
if "Ventas" in df_group.columns and "Costos" in df_group.columns:
    df_group["Ganancia"] = df_group["Ventas"] - df_group["Costos"]

col1, col2, col3 = st.columns(3)

if "Ventas" in df_group.columns:
    col1.metric("Ventas totales", round(df_group["Ventas"].sum(), 2))

if "Costos" in df_group.columns:
    col2.metric("Costos totales", round(df_group["Costos"].sum(), 2))

if "Ganancia" in df_group.columns:
    col3.metric("Ganancia total", round(df_group["Ganancia"].sum(), 2))

# -------------------------
# Datos
# -------------------------
st.subheader("📊 Datos agrupados")
st.dataframe(df_group)

# -------------------------
# Gráfica
# -------------------------
st.subheader("📈 Gráfica")

cols_plot = list(col_valores)

if "Ventas" in df_group.columns and "Costos" in df_group.columns:
    if "Ventas" in cols_plot and "Costos" in cols_plot:
        cols_plot.append("Ganancia")

if len(cols_plot) == 0:
    st.warning("Selecciona al menos una métrica")
else:
    st.line_chart(df_group.set_index("Periodo")[cols_plot])

# -------------------------
# Descargar
# -------------------------
st.download_button(
    "📥 Descargar datos",
    df_group.to_csv(index=False),
    "resultado.csv",
    "text/csv"
)
