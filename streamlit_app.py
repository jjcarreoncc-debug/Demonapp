import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Fechas OK", layout="wide")

st.title("📊 Dashboard por Fecha (corregido)")

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
# Elegir columna numérica
# -------------------------
col_valor = st.selectbox("Columna a analizar", df.columns)

df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce")

# -------------------------
# Selección tipo fecha
# -------------------------
tipo = st.sidebar.selectbox("Agrupar por", ["Día", "Mes", "Año"])

# -------------------------
# Crear Periodo (FORMA CORRECTA 🔥)
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
df_group = df.groupby("Periodo")[col_valor].sum().reset_index()

# -------------------------
# Ordenar correctamente
# -------------------------
df_group = df_group.sort_values("Periodo")

# -------------------------
# Mostrar datos
# -------------------------
st.subheader("📊 Datos agrupados")
st.dataframe(df_group)

# -------------------------
# Gráfica (YA FUNCIONA 🔥)
# -------------------------
st.subheader("📈 Gráfica")

st.line_chart(df_group.set_index("Periodo"))
