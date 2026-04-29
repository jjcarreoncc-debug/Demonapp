import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

st.title("📊 Dashboard Ejecutivo de Ventas")

# -------------------------
# CARGA ARCHIVO
# -------------------------
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:

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

    rango_fecha = st.sidebar.date_input("Rango de Fecha", [fecha_min, fecha_max])

    paises = df["Pais"].unique() if "Pais" in df.columns else []
    regiones = df["Region"].unique() if "Region" in df.columns else []
    productos = df["Producto"].unique() if "Producto" in df.columns else []

    paises_sel = st.sidebar.multiselect("País", paises, default=paises)
    regiones_sel = st.sidebar.multiselect("Región", regiones, default=regiones)
    productos_sel = st.sidebar.multiselect("Producto", productos, default=productos)

    # -------------------------
    # FILTROS
    # -------------------------
    if len(rango_fecha) == 2:
        df = df[
            (df["Fecha"] >= pd.to_datetime(rango_fecha[0])) &
            (df["Fecha"] <= pd.to_datetime(rango_fecha[1]))
        ]

    if len(paises_sel) > 0:
        df = df[df["Pais"].isin(paises_sel)]

    if len(regiones_sel) > 0:
        df = df[df["Region"].isin(regiones_sel)]

    if len(productos_sel) > 0:
        df = df[df["Producto"].isin(productos_sel)]

    # -------------------------
    # CÁLCULOS
    # -------------------------
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    ventas_total = df["Ventas"].sum()
    ganancia_total = df["Ganancia"].sum()
    margen = 0 if ventas_total == 0 else (ganancia_total / ventas_total) * 100

    # -------------------------
    # 🎯 KPIs PRINCIPALES
    # -------------------------
    st.markdown("## 🎯 KPIs Consolidados")

    col1, col2, col3 = st.columns(3)

    def gauge(valor, meta, titulo, color):
        return go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=valor,
            delta={'reference': meta},
            title={'text': titulo},
            gauge={
                'axis': {'range': [0, meta]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, meta*0.6], 'color': "red"},
                    {'range': [meta*0.6, meta*0.9], 'color': "yellow"},
                    {'range': [meta*0.9, meta], 'color': "green"}
                ],
                'threshold': {'line': {'color': "black", 'width': 3}, 'value': meta}
            }
        ))

    col1.plotly_chart(gauge(ventas_total, ventas_total*1.2, "Ventas", "blue"), use_container_width=True)
    col2.plotly_chart(gauge(ganancia_total, ganancia_total*1.2, "Ganancia", "green"), use_container_width=True)
    col3.plotly_chart(gauge(margen, 100, "Margen %", "orange"), use_container_width=True)

    # -------------------------
    # 🚨 ALERTAS AUTOMÁTICAS
    # -------------------------
    st.markdown("---")
    st.subheader("🚨 Alertas")

    if margen < 30:
        st.error(f"Margen bajo: {round(margen,1)}%")

    if ventas_total < df["Ventas"].mean() * len(df):
        st.warning("Ventas por debajo del promedio")

    if margen > 60:
        st.success("Buen nivel de rentabilidad")

    # -------------------------
    # 🌎 KPIs POR PAÍS
    # -------------------------
    if "Pais" in df.columns:

        st.markdown("---")
        st.subheader("🌎 Margen por País")

        df_pais = df.groupby("Pais")[["Ventas", "Ganancia"]].sum().reset_index()
        df_pais["Margen"] = df_pais["Ganancia"] / df_pais["Ventas"] * 100

        cols = st.columns(min(4, len(df_pais)))

        for i, row in df_pais.iterrows():
            with cols[i % len(cols)]:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=row["Margen"],
                    title={'text': row["Pais"]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'steps': [
                            {'range': [0, 30], 'color': "red"},
                            {'range': [30, 60], 'color': "yellow"},
                            {'range': [60, 100], 'color': "green"}
                        ]
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # 🗺️ KPIs POR REGIÓN
    # -------------------------
    if "Region" in df.columns:

        st.markdown("---")
        st.subheader("🗺️ Margen por Región")

        df_region = df.groupby("Region")[["Ventas", "Ganancia"]].sum().reset_index()
        df_region["Margen"] = df_region["Ganancia"] / df_region["Ventas"] * 100

        cols = st.columns(min(4, len(df_region)))

        for i, row in df_region.iterrows():
            with cols[i % len(cols)]:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=row["Margen"],
                    title={'text': row["Region"]},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'steps': [
                            {'range': [0, 30], 'color': "red"},
                            {'range': [30, 60], 'color': "yellow"},
                            {'range': [60, 100], 'color': "green"}
                        ]
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # 📈 GRÁFICA PRINCIPAL
    # -------------------------
    st.markdown("---")
    st.subheader("📈 Tendencia")

    vista = st.sidebar.radio("Métrica", ["Ventas", "Ganancia", "Ambos"])

    if vista == "Ventas":
        y_data = ["Ventas"]
    elif vista == "Ganancia":
        y_data = ["Ganancia"]
    else:
        y_data = ["Ventas", "Ganancia"]

    df_group = df.groupby("Periodo")[y_data].sum().reset_index()

    fig = px.line(df_group, x="Periodo", y=y_data, markers=True)
    fig.update_layout(hovermode="x unified")

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # DATOS
    # -------------------------
    st.markdown("---")
    with st.expander("📂 Ver datos"):
        st.dataframe(df)

else:
    st.info("📂 Sube un archivo Excel para comenzar")
