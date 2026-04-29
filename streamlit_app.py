import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")
st.title("📊 Dashboard Ejecutivo de Ventas")

# -------------------------
# CACHE
# -------------------------
@st.cache_data
def cargar_datos(archivo):
    df = pd.read_excel(archivo)
    df.columns = df.columns.str.strip()
    return df

# -------------------------
# CARGA ARCHIVO
# -------------------------
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:

    df = cargar_datos(archivo)

    # -------------------------
    # VALIDACIONES
    # -------------------------
    columnas_necesarias = ["Fecha", "Ventas", "Costos"]

    for col in columnas_necesarias:
        if col not in df.columns:
            st.error(f"Falta la columna obligatoria: {col}")
            st.stop()

    # -------------------------
    # LIMPIEZA
    # -------------------------
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

    # -------------------------
    # SIDEBAR (FILTROS)
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
    # APLICAR FILTROS
    # -------------------------
    if isinstance(rango_fecha, list) and len(rango_fecha) == 2:
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
    # CONTROL DATA VACÍA
    # -------------------------
    if df.empty:
        st.warning("No hay datos con los filtros seleccionados")
        st.stop()

    # -------------------------
    # CÁLCULOS
    # -------------------------
    df["Ganancia"] = df["Ventas"] - df["Costos"]
    df["Periodo"] = df["Fecha"].dt.to_period("M").astype(str)

    ventas_total = df["Ventas"].sum()
    ganancia_total = df["Ganancia"].sum()
    margen = 0 if ventas_total == 0 else (ganancia_total / ventas_total) * 100

    # -------------------------
    # KPIs
    # -------------------------
    st.markdown("## 🎯 KPIs")

    col1, col2, col3 = st.columns(3)

    prom_ventas = df.groupby("Pais")["Ventas"].sum().mean() if "Pais" in df.columns else ventas_total
    prom_ganancia = df.groupby("Pais")["Ganancia"].sum().mean() if "Pais" in df.columns else ganancia_total

    prom_ventas = np.nan_to_num(prom_ventas)
    prom_ganancia = np.nan_to_num(prom_ganancia)

    def kpi(valor, referencia, titulo):
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=valor,
            delta={'reference': referencia, 'relative': True},
            title={'text': titulo}
        ))
        return fig

    col1.plotly_chart(kpi(ventas_total, prom_ventas, "Ventas"), use_container_width=True)
    col2.plotly_chart(kpi(ganancia_total, prom_ganancia, "Ganancia"), use_container_width=True)

    # -------------------------
    # GAUGE MARGEN
    # -------------------------
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=margen,
        delta={'reference': 50},
        title={'text': "Margen %"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "#e74c3c"},
                {'range': [30, 60], 'color': "#f1c40f"},
                {'range': [60, 100], 'color': "#2ecc71"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'value': 50
            }
        }
    ))

    col3.plotly_chart(fig_gauge, use_container_width=True)

    # -------------------------
    # ALERTAS
    # -------------------------
    st.markdown("---")
    st.subheader("🚨 Alertas")

    if margen < 30:
        st.error(f"Margen bajo: {round(margen,1)}%")
    elif margen > 60:
        st.success("Alta rentabilidad")
    else:
        st.info("Margen en rango medio")

    # -------------------------
    # RANKING PAÍS
    # -------------------------
    if "Pais" in df.columns:

        st.markdown("---")
        st.subheader("🏆 Ranking País")

        df_rank = df.groupby("Pais")["Ventas"].sum().sort_values().reset_index()

        fig = px.bar(df_rank, x="Ventas", y="Pais", orientation="h", text="Ventas")

        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')

        fig.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            yaxis_title="",
            xaxis_title="Ventas"
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # RANKING REGIÓN
    # -------------------------
    if "Region" in df.columns:

        st.markdown("---")
        st.subheader("🗺️ Ranking Región")

        df_rank_r = df.groupby("Region")["Ventas"].sum().sort_values().reset_index()

        fig_r = px.bar(df_rank_r, x="Ventas", y="Region", orientation="h", text="Ventas")

        fig_r.update_traces(texttemplate='%{text:,.0f}', textposition='outside')

        fig_r.update_layout(
            showlegend=False,
            plot_bgcolor="white",
            yaxis_title="",
            xaxis_title="Ventas"
        )

        st.plotly_chart(fig_r, use_container_width=True)

    # -------------------------
    # TENDENCIA
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
    df_group = df_group.sort_values("Periodo")

    fig_line = px.line(df_group, x="Periodo", y=y_data, markers=True)
    fig_line.update_layout(hovermode="x unified")

    st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------
    # INSIGHTS AUTOMÁTICOS
    # -------------------------
    st.markdown("---")
    st.subheader("🧠 Insights Automáticos")

    if len(df_group) > 1:
        ultimo = df_group.iloc[-1]["Ventas"]
        anterior = df_group.iloc[-2]["Ventas"]

        variacion = ((ultimo - anterior) / anterior) * 100 if anterior != 0 else 0

        if variacion > 0:
            st.success(f"📈 Las ventas crecieron {variacion:.1f}% vs periodo anterior")
        else:
            st.error(f"📉 Las ventas cayeron {abs(variacion):.1f}% vs periodo anterior")

    # -------------------------
    # DATOS
    # -------------------------
    st.markdown("---")
    with st.expander("📂 Ver datos"):
        st.dataframe(df)

else:
    st.info("📂 Sube un archivo Excel para comenzar")
