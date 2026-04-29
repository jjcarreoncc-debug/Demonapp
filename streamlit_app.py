import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard con Agrupaciones", layout="wide")

st.title("📊 Dashboard con Agrupaciones")

# -------------------------
# Cargar archivo
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
st.subheader("📋 Datos originales")
st.dataframe(df)

# -------------------------
# Sidebar configuración
# -------------------------
st.sidebar.header("⚙️ Configuración")

columna_grupo = st.sidebar.selectbox("Agrupar por", df.columns)
columna_valor = st.sidebar.selectbox("Valor a analizar", df.columns)

tipo_agrupacion = st.sidebar.selectbox(
    "Tipo de agrupación",
    ["Suma", "Promedio", "Conteo"]
)

# -------------------------
# Agrupación
# -------------------------
if tipo_agrupacion == "Suma":
    df_group = df.groupby(columna_grupo)[columna_valor].sum()
elif tipo_agrupacion == "Promedio":
    df_group = df.groupby(columna_grupo)[columna_valor].mean()
else:
    df_group = df.groupby(columna_grupo)[columna_valor].count()

df_group = df_group.reset_index()

# -------------------------
# Mostrar resultado
# -------------------------
st.subheader("📊 Datos agrupados")
st.dataframe(df_group)

# -------------------------
# Métrica principal
# -------------------------
if pd.api.types.is_numeric_dtype(df_group[columna_valor]):
    st.metric("Valor total", round(df_group[columna_valor].sum(), 2))

# -------------------------
# Gráfica
# -------------------------
st.subheader("📈 Gráfica")

try:
    df_plot = df_group.set_index(columna_grupo)
    st.bar_chart(df_plot)
except:
    st.error("No se pudo generar la gráfica")

# -------------------------
# Descargar
# -------------------------
st.download_button(
    "📥 Descargar datos agrupados",
    df_group.to_csv(index=False),
    "datos_agrupados.csv",
    "text/csv"
)
