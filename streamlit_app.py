import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo PRO", layout="wide")
st.title("📊 Dashboard Ejecutivo PRO")

# -------------------------
# CACHE
# -------------------------
@st.cache_data
def cargar_datos(archivo):
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()
    return df

# -------------------------
# VALIDACIÓN + PREPARACIÓN
# -------------------------
def validar(df):
    for col in ["Fecha", "Ventas", "Costos"]:
        if col not in df.columns:
            st.error(f"Falta columna: {col}")
            st.stop()

def preparar(df):
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)
    return df

# -------------------------
# CARGA
# -------------------------
archivo = st.file_uploader("Sube tu Excel", type=["xlsx"])

if archivo:

    df = cargar_datos(archivo)
    validar(df)
    df = preparar(df)

    # -------------------------
    # FILTROS
    # -------------------------
    st.sidebar.header("🔎 Filtros")

    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    rango = st.sidebar.date_input("Rango de fecha", [fecha_min, fecha_max])

    paises = df["Pais"].dropna().unique() if "Pais" in df.columns else []
    regiones = df["Region"].dropna().unique() if "Region" in df.columns else []
    productos = df["Producto"].dropna().unique() if "Producto" in df.columns else []

    pais_sel = st.sidebar.multiselect("País", paises, default=paises)
    reg_sel = st.sidebar.multiselect("Región", regiones, default=regiones)
    prod_sel = st.sidebar.multiselect("Producto", productos, default=productos)

    # Aplicar filtros
    if isinstance(rango, list) and len(rango) == 2:
        df = df[(df["Fecha"] >= pd.to_datetime(rango[0])) &
                (df["Fecha"] <= pd.to_datetime(rango[1]))]

    if len(pais_sel) > 0:
        df = df[df["Pais"].isin(pais_sel)]

    if len(reg_sel) > 0:
        df = df[df["Region"].isin(reg_sel)]

    if len(prod_sel) > 0:
        df = df[df["Producto"].isin(prod_sel)]

    if df.empty:
        st.warning("Sin datos con esos filtros")
        st.stop()

    # -------------------------
    # KPIs
    # -------------------------
    ventas = df["Ventas"].sum()
    ganancia = df["Ganancia"].sum()
    margen = 0 if ventas == 0 else (ganancia / ventas) * 100

    df_m = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index().sort_values("Periodo")

    if len(df_m) > 1:
        var = ((df_m.iloc[-1]["Ventas"] - df_m.iloc[-2]["Ventas"]) /
               df_m.iloc[-2]["Ventas"]) * 100
    else:
        var = 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Ventas", f"${ventas:,.0f}", f"{var:.1f}%")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    # Gauge
    fig_g = go.Figure(go.Indicator(
        mode="gauge+number",
        value=margen,
        title={'text': "Margen %"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 30], 'color': "#e74c3c"},
                {'range': [30, 60], 'color': "#f1c40f"},
                {'range': [60, 100], 'color': "#2ecc71"}
            ]
        }
    ))
    c4.plotly_chart(fig_g, use_container_width=True)

    # -------------------------
    # TOP PAÍSES (TARJETAS)
    # -------------------------
    if "Pais" in df.columns:
        st.markdown("### 🏆 Top Países")

        df_top = df.groupby("Pais")["Ventas"].sum().sort_values(ascending=False).head(5).reset_index()

        cols = st.columns(len(df_top))
        for i, row in df_top.iterrows():
            cols[i].metric(row["Pais"], f"${row['Ventas']:,.0f}")

    # -------------------------
    # DONUT REGIÓN
    # -------------------------
    if "Region" in df.columns:
        st.markdown("### 🌍 Distribución por Región")

        df_region = df.groupby("Region")["Ventas"].sum().reset_index()

        fig_donut = px.pie(df_region, names="Region", values="Ventas", hole=0.6)
        fig_donut.update_traces(textinfo="percent+label")

        st.plotly_chart(fig_donut, use_container_width=True)

    # -------------------------
    # TENDENCIA
    # -------------------------
    st.markdown("### 📈 Tendencia de Negocio")

    fig_line = px.line(
        df_m,
        x="Periodo",
        y=["Ventas", "Ganancia"],
        markers=True
    )

    fig_line.update_layout(
        hovermode="x unified",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------
    # INSIGHTS
    # -------------------------
    st.markdown("### 🧠 Insight Ejecutivo")

    if len(df_m) > 2:
        crecimiento = df_m["Ventas"].pct_change().mean() * 100

        if crecimiento > 0:
            st.success(f"Crecimiento promedio mensual: {crecimiento:.1f}%")
        else:
            st.error(f"Tendencia negativa: {crecimiento:.1f}%")

    # -------------------------
    # DATOS
    # -------------------------
    with st.expander("📂 Ver datos"):
        st.dataframe(df)

else:
    st.info("Sube archivo Excel")
