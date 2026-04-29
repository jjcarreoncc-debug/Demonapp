import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    # FILTROS
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

    # combinación
    if all(col in df.columns for col in ["Pais", "Region", "Producto"]):
        df["Categoria"] = (
            df["Pais"].astype(str) + " | " +
            df["Region"].astype(str) + " | " +
            df["Producto"].astype(str)
        )

    # -------------------------
    # KPIs NUMÉRICOS
    # -------------------------
    st.subheader("📊 KPIs")

    ventas_total = df["Ventas"].sum()
    ganancia_total = df["Ganancia"].sum()
    costos_total = df["Costos"].sum()

    margen = 0 if ventas_total == 0 else (ganancia_total / ventas_total) * 100

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Ventas", round(ventas_total, 0))
    k2.metric("Ganancia", round(ganancia_total, 0))
    k3.metric("Costos", round(costos_total, 0))
    k4.metric("Margen %", round(margen, 1))

    # -------------------------
    # 🎯 GAUGES (CÍRCULOS)
    # -------------------------
    st.markdown("---")
    st.subheader("🎯 Indicadores Visuales")

    g1, g2, g3 = st.columns(3)

    # Ventas
    max_v = df["Ventas"].max() if not df.empty else 1
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ventas_total,
        title={'text': "Ventas"},
        gauge={
            'axis': {'range': [0, max_v]},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [0, max_v*0.5], 'color': "lightgray"},
                {'range': [max_v*0.5, max_v], 'color': "green"}
            ]
        }
    ))
    g1.plotly_chart(fig1, use_container_width=True)

    # Ganancia
    max_g = df["Ganancia"].max() if not df.empty else 1
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ganancia_total,
        title={'text': "Ganancia"},
        gauge={
            'axis': {'range': [0, max_g]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, max_g*0.5], 'color': "lightgray"},
                {'range': [max_g*0.5, max_g], 'color': "lime"}
            ]
        }
    ))
    g2.plotly_chart(fig2, use_container_width=True)

    # Margen
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=margen,
        title={'text': "Margen %"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "orange"},
            'steps': [
                {'range': [0, 30], 'color': "red"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "green"}
            ]
        }
    ))
    g3.plotly_chart(fig3, use_container_width=True)

    # -------------------------
    # 📈 GRÁFICA PRINCIPAL
    # -------------------------
    st.markdown("---")
    st.subheader("📈 Evolución País | Región | Producto")

    if "Categoria" in df.columns:

        df_combo = (
            df.groupby(["Periodo", "Categoria"])["Ventas"]
            .sum()
            .reset_index()
        )

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
        st.warning("Faltan columnas: Pais, Region o Producto")

    # -------------------------
    # DATOS
    # -------------------------
    st.markdown("---")
    with st.expander("📂 Ver datos"):
        st.dataframe(df)

else:
    st.info("📂 Sube un archivo Excel para comenzar")
