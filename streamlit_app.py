import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard BI", layout="wide")

st.title("📊 Dashboard Ejecutivo de Ventas")
st.markdown("### Análisis de Ventas y Rentabilidad")
st.markdown("---")

# -------------------------
# CARGA ARCHIVO
# -------------------------
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:

    # -------------------------
    # LECTURA
    # -------------------------
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    # -------------------------
    # SIDEBAR (FILTROS)
    # -------------------------
    st.sidebar.header("🔎 Filtros")

    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    rango_fecha = st.sidebar.date_input(
        "Rango de Fecha",
        [fecha_min, fecha_max]
    )

    if "Pais" in df.columns:
        paises = st.sidebar.multiselect(
            "País",
            df["Pais"].unique(),
            default=df["Pais"].unique()
        )
    else:
        paises = None

    if "Region" in df.columns:
        regiones = st.sidebar.multiselect(
            "Región",
            df["Region"].unique(),
            default=df["Region"].unique()
        )
    else:
        regiones = None

    if "Producto" in df.columns:
        productos = st.sidebar.multiselect(
            "Producto",
            df["Producto"].unique(),
            default=df["Producto"].unique()
        )
    else:
        productos = None

    # -------------------------
    # APLICAR FILTROS
    # -------------------------
    if len(rango_fecha) == 2:
        df = df[
            (df["Fecha"] >= pd.to_datetime(rango_fecha[0])) &
            (df["Fecha"] <= pd.to_datetime(rango_fecha[1]))
        ]

    if paises:
        df = df[df["Pais"].isin(paises)]

    if regiones:
        df = df[df["Region"].isin(regiones)]

    if productos:
        df = df[df["Producto"].isin(productos)]

    # -------------------------
    # CÁLCULOS
    # -------------------------
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    # 🧠 COMBINACIÓN CLAVE
    if all(col in df.columns for col in ["Pais", "Region", "Producto"]):
        df["Categoria"] = (
            df["Pais"].astype(str) + " | " +
            df["Region"].astype(str) + " | " +
            df["Producto"].astype(str)
        )

    # -------------------------
    # KPIs
    # -------------------------
    st.subheader("📊 KPIs")

    ventas_total = df["Ventas"].sum()
    ganancia_total = df["Ganancia"].sum()

    margen = 0 if ventas_total == 0 else (ganancia_total / ventas_total) * 100

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Ventas", round(ventas_total, 0))
    col2.metric("📈 Ganancia", round(ganancia_total, 0))
    col3.metric("📊 Margen %", round(margen, 1))

    # -------------------------
    # 🎯 CONTROL TOP
    # -------------------------
    st.sidebar.markdown("---")
    top_n = st.sidebar.slider("Top categorías", 5, 20, 10)

    # -------------------------
    # 📊 GRÁFICA PRINCIPAL
    # -------------------------
    st.markdown("---")
    st.subheader("📈 Evolución País | Región | Producto")

    if "Categoria" in df.columns:

        df_combo = (
            df.groupby(["Periodo", "Categoria"])["Ventas"]
            .sum()
            .reset_index()
        )

        # 🔥 TOP CATEGORÍAS
        top_cat = (
            df.groupby("Categoria")["Ventas"]
            .sum()
            .nlargest(top_n)
            .index
        )

        df_combo = df_combo[df_combo["Categoria"].isin(top_cat)]

        fig = px.line(
            df_combo,
            x="Periodo",
            y="Ventas",
            color="Categoria",
            markers=True
        )

        fig.update_layout(hovermode="x unified")

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Se requieren columnas: Pais, Region y Producto")

    # -------------------------
    # DATOS
    # -------------------------
    st.markdown("---")
    with st.expander("📂 Ver datos"):
        st.dataframe(df)

else:
    st.info("📂 Sube un archivo Excel para comenzar")
