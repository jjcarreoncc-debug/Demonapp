import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
# VALIDACIÓN
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
    # FILTROS INTELIGENTES
    # -------------------------
    st.sidebar.header("🔎 Filtros Inteligentes")

    # FECHA
    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    rango = st.sidebar.date_input("Rango de fecha", [fecha_min, fecha_max])

    df_filtrado = df.copy()

    # PAÍS
    if "Pais" in df.columns:
        paises = sorted(df["Pais"].dropna().unique())
        pais_sel = st.sidebar.multiselect("País", paises, default=paises)
        if pais_sel:
            df_filtrado = df_filtrado[df_filtrado["Pais"].isin(pais_sel)]

    # REGIÓN DEPENDE DE PAÍS
    if "Region" in df.columns:
        regiones = sorted(df_filtrado["Region"].dropna().unique())
        reg_sel = st.sidebar.multiselect("Región", regiones, default=regiones)
        if reg_sel:
            df_filtrado = df_filtrado[df_filtrado["Region"].isin(reg_sel)]

    # NOMBRE DEPENDE DE REGIÓN
    if "Nombre" in df.columns:
        nombres = sorted(df_filtrado["Nombre"].dropna().unique())
        nom_sel = st.sidebar.multiselect("Nombre", nombres, default=nombres)
        if nom_sel:
            df_filtrado = df_filtrado[df_filtrado["Nombre"].isin(nom_sel)]

    # FECHA AL FINAL
    if isinstance(rango, list) and len(rango) == 2:
        df_filtrado = df_filtrado[
            (df_filtrado["Fecha"] >= pd.to_datetime(rango[0])) &
            (df_filtrado["Fecha"] <= pd.to_datetime(rango[1]))
        ]

    if df_filtrado.empty:
        st.warning("Sin datos con esos filtros")
        st.stop()

    df = df_filtrado

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

    # GAUGE
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
    # TOP PAÍSES
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

    fig_line = px.line(df_m, x="Periodo", y=["Ventas", "Ganancia"], markers=True)
    fig_line.update_layout(hovermode="x unified", plot_bgcolor="white")

    st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------
    # INSIGHT
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

# -------------------------
# IA - INSIGHTS AUTOMÁTICOS AVANZADOS
# -------------------------
st.markdown("### 🤖 Análisis Inteligente")

# 1. CRECIMIENTO
if len(df_m) > 2:
    crecimiento = df_m["Ventas"].pct_change().mean() * 100

    if crecimiento > 0:
        st.success(f"📈 Tendencia positiva: crecimiento promedio {crecimiento:.1f}% mensual")
    else:
        st.error(f"📉 Tendencia negativa: caída promedio {crecimiento:.1f}% mensual")

# 2. QUÉ EXPLICA LAS VENTAS
if "Region" in df.columns:
    df_region = df.groupby("Region")["Ventas"].sum().sort_values(ascending=False)

    top_region = df_region.index[0]
    share = (df_region.iloc[0] / df_region.sum()) * 100

    st.info(f"🌍 La región {top_region} genera el {share:.1f}% de las ventas")

# 3. CONCENTRACIÓN (RIESGO NEGOCIO)
if "Nombre" in df.columns:
    df_nombre = df.groupby("Nombre")["Ventas"].sum().sort_values(ascending=False)

    top_nombre = df_nombre.index[0]
    share_nombre = (df_nombre.iloc[0] / df_nombre.sum()) * 100

    if share_nombre > 40:
        st.warning(f"⚠️ Alta dependencia: {top_nombre} genera {share_nombre:.1f}% del total")
    else:
        st.success("Distribución saludable entre responsables")

# 4. ALERTA DE MARGEN
if margen < 30:
    st.error("💰 Problema: margen bajo, revisar costos")
elif margen > 60:
    st.success("💰 Excelente rentabilidad")

# 5. VARIABILIDAD
volatilidad = df_m["Ventas"].std()

if volatilidad > df_m["Ventas"].mean() * 0.3:
    st.warning("📊 Alta variabilidad en ventas (inestabilidad)")
else:
    st.success("📊 Ventas estables")
else:
    st.info("Sube archivo Excel")
