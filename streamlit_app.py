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
if archivo.name.endswith(".csv"):
    df = pd.read_csv(archivo)
else:
    df = pd.read_excel(archivo)

# 🔥 optimización
df = df.head(500)
df = df[["Fecha", "Ventas", "Costos"]]

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

# -------------------------
# KPIs
# -------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Ventas", round(df_group["Ventas"].sum(), 2))
col2.metric("💸 Costos", round(df_group["Costos"].sum(), 2))
col3.metric("📈 Ganancia", round(df_group["Ganancia"].sum(), 2))
col4.metric("📊 Margen %", round(df_group["Margen %"].mean(), 2))

# -------------------------
# Gráfica
# -------------------------
st.subheader("📈 Tendencia")

st.line_chart(
    df_group.set_index("Periodo")[["Ventas", "Costos", "Ganancia"]]
)

# -------------------------
# Tabla
# -------------------------
st.subheader("📊 Datos")
st.dataframe(df_group)

# -------------------------
# DESCARGA 🔥
# -------------------------
csv = df_group.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Descargar resultados",
    data=csv,
    file_name="dashboard_resultados.csv",
    mime="text/csv"
)
