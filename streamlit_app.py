import streamlit as st
import pandas as pd
import plotly.express as px
import time

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
    # SIDEBAR
    # -------------------------
    st.sidebar.header("🔎 Filtros")

    # FILTRO FECHA
    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    rango_fecha = st.sidebar.date_input(
        "Rango de Fecha",
        [fecha_min, fecha_max]
    )

    # 🌎 FILTRO PAÍS
    if "Pais" in df.columns:
        paises = st.sidebar.multiselect(
            "País",
            df["Pais"].unique(),
            default=df["Pais"].unique()
        )
    else:
        paises = None

    # 🗺️ FILTRO REGIÓN
    if "Region" in df.columns:
        regiones = st.sidebar.multiselect(
            "Región",
            df["Region"].unique(),
            default=df["Region"].unique()
        )
    else:
        regiones = None

    # 📦 PRODUCTO
    if "Producto" in df.columns:
        productos = st.sidebar.multiselect(
            "Producto",
            df["Producto"].unique(),
            default=df["Producto"].unique()
        )
    else:
        productos = None

    # 👤 CLIENTE
    if "Nombre" in df.columns:
        clientes = st.sidebar.multiselect(
            "Cliente",
            df["Nombre"].unique(),
            default=df["Nombre"].unique()
        )
    else:
        clientes = None

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

    if clientes:
        df = df[df["Nombre"].isin(clientes)]

    # -------------------------
    # CÁLCULOS
    # -------------------------
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    df_group = (
        df.groupby("Periodo")[["Ventas", "Ganancia"]]
        .sum()
        .reset_index()
        .sort_values("Periodo")
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
    # EVOLUCIÓN
    # -------------------------
    st.markdown("---")
    st.subheader("📈 Evolución")

    fig = px.line(
        df_group,
        x="Periodo",
        y=["Ventas", "Ganancia"],
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # 🌎 VENTAS POR PAÍS
    # -------------------------
    if "Pais" in df.columns:
        st.markdown("---")
        st.subheader("🌎 Ventas por País")

        ventas_pais = (
            df.groupby("Pais")["Ventas"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_pais = px.bar(
            ventas_pais,
            x="Pais",
            y="Ventas",
            color="Ventas"
        )

        st.plotly_chart(fig_pais, use_container_width=True)

    # -------------------------
    # 🗺️ VENTAS POR REGIÓN
    # -------------------------
    if "Region" in df.columns:
        st.markdown("---")
        st.subheader("🗺️ Ventas por Región")

        ventas_region = (
            df.groupby("Region")["Ventas"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_region = px.bar(
            ventas_region,
            x="Region",
            y="Ventas",
            color="Ventas"
        )

        st.plotly_chart(fig_region, use_container_width=True)

    # -------------------------
    # DATOS
    # -------------------------
    st.markdown("---")
    with st.expander("📂 Ver datos"):
        st.dataframe(df)

else:
    st.info("📂 Sube un archivo Excel para comenzar")
