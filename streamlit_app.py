import streamlit as st
import pandas as pd

# Configuración
st.set_page_config(page_title="Dashboard Excel", layout="wide")

st.title("📊 Dashboard desde Excel")

# -------------------------
# Subir archivo
# -------------------------
archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx", "csv"])

if archivo is not None:
    if archivo.name.endswith(".csv"):
        df = pd.read_csv(archivo)
    else:
        df = pd.read_excel(archivo)
else:
    st.warning("⚠️ Sube un archivo para continuar")
    st.stop()

# -------------------------
# Mostrar datos
# -------------------------
st.subheader("📋 Datos")
st.dataframe(df)

# -------------------------
# Selección de columnas
# -------------------------
st.sidebar.header("⚙️ Configuración")

columna_x = st.sidebar.selectbox("Selecciona eje X", df.columns)
columna_y = st.sidebar.selectbox("Selecciona eje Y", df.columns)

# -------------------------
# Métricas
# -------------------------
if pd.api.types.is_numeric_dtype(df[columna_y]):
    st.metric("Promedio", round(df[columna_y].mean(), 2))

# -------------------------
# Gráfica
# -------------------------
st.subheader("📈 Gráfica")

try:
    df_plot = df[[columna_x, columna_y]].dropna()
    df_plot = df_plot.set_index(columna_x)
    st.line_chart(df_plot)
except:
    st.error("No se pudo generar la gráfica")
# -------------------------
# Filtro opcional
# -------------------------
st.subheader("🔎 Filtro")

if pd.api.types.is_numeric_dtype(df[columna_y]):
    min_val = float(df[columna_y].min())
    max_val = float(df[columna_y].max())

    rango = st.slider("Filtrar valores", min_val, max_val, (min_val, max_val))

    df
