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
    # KPIs CON CONTEXTO
    # -------------------------
    st.markdown("## 🎯 KPIs con Contexto")

    col1, col2, col3 = st.columns(3)

    prom_ventas = df.groupby("Pais")["Ventas"].sum().mean() if "Pais" in df.columns else ventas_total
    prom_ganancia = df.groupby("Pais")["Ganancia"].sum().mean() if "Pais" in df.columns else ganancia_total

    def kpi(valor, referencia, titulo, subtitulo):
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=valor,
            delta={'reference': referencia, 'relative': True},
            title={'text': f"{titulo}<br><span style='font-size:12px'>{subtitulo}</span>"}
        ))
        return fig

    col1.plotly_chart(kpi(ventas_total, prom_ventas, "Ventas", "vs promedio país"), use_container_width=True)
    col2.plotly_chart(kpi(ganancia_total, prom_ganancia, "Ganancia", "vs promedio país"), use_container_width=True)
    col3.plotly_chart(kpi(margen, 50, "Margen %", "vs objetivo 50%"), use_container_width=True)

    # -------------------------
    # ALERTAS
    # -------------------------
    st.markdown("---")
    st.subheader("🚨 Alertas")

    if margen < 30:
        st.error(f"Margen bajo: {round(margen,1)}%")

    if margen > 60:
        st.success("Alta rentabilidad")

    # -------------------------
    # RANKING PAÍS
    # -------------------------
    if "Pais" in df.columns:

        st.markdown("---")
        st.subheader("🏆 Ranking País")

        df_rank = df.groupby("Pais")["Ventas"].sum().sort_values().reset_index()

        mejor = df_rank.iloc[-1]["Pais"]
        peor = df_rank.iloc[0]["Pais"]

        df_rank["Color"] = df_rank["Pais"].apply(
            lambda x: "green" if x == mejor else ("red" if x == peor else "blue")
        )

        fig = px.bar(
            df_rank,
            x="Ventas",
            y="Pais",
            orientation="h",
            color="Color",
            color_discrete_map={"green": "green", "red": "red", "blue": "lightblue"}
        )

        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"🏆 Mejor: {mejor} | 🔻 Peor: {peor}")

    # -------------------------
    # RANKING REGIÓN
    # -------------------------
    if "Region" in df.columns:

        st.markdown("---")
        st.subheader("🗺️ Ranking Región")

        df_rank_r = df.groupby("Region")["Ventas"].sum().sort_values().reset_index()

        mejor_r = df_rank_r.iloc[-1]["Region"]
        peor_r = df_rank_r.iloc[0]["Region"]

        df_rank_r["Color"] = df_rank_r["Region"].apply(
            lambda x: "green" if x == mejor_r else ("red" if x == peor_r else "blue")
        )

        fig_r = px.bar(
            df_rank_r,
            x="Ventas",
            y="Region",
            orientation="h",
            color="Color",
            color_discrete_map={"green": "green", "red": "red", "blue": "lightblue"}
        )

        st.plotly_chart(fig_r, use_container_width=True)
        st.caption(f"🏆 Mejor: {mejor_r} | 🔻 Peor: {peor_r}")

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

    fig_line = px.line(df_group, x="Periodo", y=y_data, markers=True)
    fig_line.update_layout(hovermode="x unified")

    st.plotly_chart(fig_line, use_container_width=True)

    # -------------------------
    # DATOS
    # -------------------------
    st.markdown("---")
    with st.expander("📂 Ver datos"):
        st.dataframe(df)

else:
    st.info("📂 Sube un archivo Excel para comenzar")
