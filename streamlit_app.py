import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard con Fechas", layout="wide")

st.title("📊 Dashboard con Análisis por Fecha")

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
# Validar columna Fecha
# -------------------------
if "Fecha" not in df.columns:
    st.error("❌ El archivo debe tener una columna llamada 'Fecha'")
    st.stop()

# -------------------------
# Convertir a fecha
# -------------------------
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

# -------------------------
# Selección de columna numérica
# -------------------------
col_valor = st.selectbox("Selecciona columna numérica", df.columns)

# Asegurar que sea numérica
df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce")

# -------------------------
# Tipo de agrupación por fecha
# -------------------------
tipo_fecha = st.sidebar.selectbox(
    "Agrupar por",
    ["Día", "Mes", "Año"]
)

# -------------------------
# Crear Periodo
# -------------------------
if tipo_fecha == "Día":
    df["Periodo"] = df["Fecha"].dt.date
elif tipo_fecha == "Mes":
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)
else:
    df["Periodo"] = df["Fecha"].dt.year

# -------------------------
# Agrupación
# -------------------------
df_group = df.groupby("Periodo")[col_valor].sum().reset_index()

# -------------------------
# ORDENAR (CLAVE 🔥)
# -------------------------
df_group = df_group.sort_values("Periodo")

# -------------------------
# Mostrar datos
# -------------------------
st.subheader("📊 Datos agrupados")
st.dataframe(df_group)

# -------------------------
# Gráfica
# -------------------------
st.subheader("📈 Gráfica")

st.line_chart(df_group.set_index("Periodo"))
