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

    if all(col in df.columns for col in ["Pais", "Region", "Producto"]):
        df["Categoria"] = (
            df["Pais"].astype(str) + " | " +
            df["Region"].astype(str) + " | " +
            df["Producto"].astype(str)
        )

    ventas_total = df["Ventas"].sum()
    ganancia_total = df["Ganancia"].sum()
    costos_total = df["Costos"].sum()

    margen = 0 if ventas_total == 0 else (ganancia_total / ventas_total) * 100

    # -------------------------
    # 🎯 KPIs INTELIGENTES
    # -------------------------
    st.subheader("🎯 KPIs con Objetivo")

    g1, g2, g3 = st.columns(3)

    # METAS (puedes ajustarlas o traerlas de Excel)
    meta_ventas = ventas_total * 1.2 if ventas_total > 0 else 1
    meta_ganancia = ganancia_total * 1.2 if ganancia_total > 0 else 1
    meta_margen = 50

    # VENTAS
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ventas_total,
        delta={'reference': meta_ventas},
        title={'text': "Ventas"},
        gauge={
            'axis': {'range': [0, meta_ventas]},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [0, meta_ventas*0.6], 'color': "red"},
                {'range': [meta_ventas*0.6, meta_ventas*0.9], 'color': "yellow"},
                {'range': [meta_ventas*0.9, meta_ventas], 'color': "green"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'value': meta_ventas}
        }
    ))
    g1.plotly_chart(fig1, use_container_width=True)

    # GANANCIA
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ganancia_total,
        delta={'reference': meta_ganancia},
        title={'text': "Ganancia"},
        gauge={
            'axis': {'range': [0, meta_ganancia]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, meta_ganancia*0.6], 'color': "red"},
                {'range': [meta_ganancia*0.6, meta_ganancia*0.9], 'color': "yellow"},
                {'range': [meta_ganancia*0.9, meta_ganancia], 'color': "green"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'value': meta_ganancia}
        }
    ))
    g2.plotly_chart(fig2, use_container_width=True)

    # MARGEN
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=margen,
        delta={'reference': meta_margen},
        title={'text': "Margen %"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "orange"},
            'steps': [
                {'range': [0, 30], 'color': "red"},
                {'range': [30, 50], 'color': "yellow"},
                {'range': [50, 100], 'color': "green"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'value': meta_margen}
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
