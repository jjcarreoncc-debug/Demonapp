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
# FUNCIONES
# -------------------------
def validar_columnas(df):
    required = ["Fecha", "Ventas", "Costos"]
    for col in required:
        if col not in df.columns:
            st.error(f"Falta columna: {col}")
            st.stop()

def preparar_datos(df):
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)
    return df

def calcular_kpis(df):
    ventas = df["Ventas"].sum()
    ganancia = df["Ganancia"].sum()
    margen = 0 if ventas == 0 else (ganancia / ventas) * 100
    return ventas, ganancia, margen

def variacion_mensual(df):
    df_group = df.groupby("Periodo")["Ventas"].sum().reset_index().sort_values("Periodo")
    if len(df_group) < 2:
        return 0
    ultimo = df_group.iloc[-1]["Ventas"]
    anterior = df_group.iloc[-2]["Ventas"]
    return ((ultimo - anterior) / anterior) * 100 if anterior != 0 else 0

# -------------------------
# CARGA
# -------------------------
archivo = st.file_uploader("Sube tu Excel", type=["xlsx"])

if archivo:

    df = cargar_datos(archivo)
    validar_columnas(df)
    df = preparar_datos(df)

    # -------------------------
    # FILTROS
    # -------------------------
    st.sidebar.header("Filtros")

    rango = st.sidebar.date_input("Fecha", [df["Fecha"].min(), df["Fecha"].max()])

    if isinstance(rango, list) and len(rango) == 2:
        df = df[(df["Fecha"] >= pd.to_datetime(rango[0])) &
                (df["Fecha"] <= pd.to_datetime(rango[1]))]

    if df.empty:
        st.warning("Sin datos")
        st.stop()

    # -------------------------
    # KPIs
    # -------------------------
    ventas, ganancia, margen = calcular_kpis(df)
    var_mensual = variacion_mensual(df)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Ventas", f"${ventas:,.0f}", f"{var_mensual:.1f}%")
    c2.metric("Ganancia", f"${ganancia:,.0f}")
    c3.metric("Margen", f"{margen:.1f}%")

    # Gauge
    fig_gauge = go.Figure(go.Indicator(
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
    c4.plotly_chart(fig_gauge, use_container_width=True)

    # -------------------------
    # INSIGHT EJECUTIVO
    # -------------------------
    st.markdown("### 🧠 Insight Ejecutivo")

    if var_mensual > 0:
        st.success(f"Ventas creciendo {var_mensual:.1f}% mensual")
    else:
        st.error(f"Ventas cayendo {abs(var_mensual):.1f}% mensual")

    # -------------------------
    # TOP VS OTROS
    # -------------------------
    if "Producto" in df.columns:
        st.markdown("### 🔝 Top Productos vs Otros")

        top = df.groupby("Producto")["Ventas"].sum().sort_values(ascending=False)
        top5 = top.head(5)
        otros = pd.Series({"Otros": top.iloc[5:].sum()})

        df_top = pd.concat([top5, otros]).reset_index()
        df_top.columns = ["Producto", "Ventas"]

        fig_top = px.pie(df_top, names="Producto", values="Ventas", hole=0.5)
        st.plotly_chart(fig_top, use_container_width=True)

    # -------------------------
    # TENDENCIA
    # -------------------------
    st.markdown("### 📈 Tendencia")

    df_group = df.groupby("Periodo")[["Ventas", "Ganancia"]].sum().reset_index()
    df_group = df_group.sort_values("Periodo")

    fig = px.line(df_group, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # TABLA
    # -------------------------
    with st.expander("Ver datos"):
        st.dataframe(df)

else:
    st.info("Sube archivo")
