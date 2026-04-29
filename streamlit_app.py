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
    # SIDEBAR
    # -------------------------
    st.sidebar.header("🔎 Filtros")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Visualización")

    vista = st.sidebar.radio(
        "Métrica",
        ["Ventas", "Ganancia", "Ambos"]
    )

    tipo = st.sidebar.radio(
        "Tipo de gráfica",
        ["Línea", "Área"]
    )

    # FILTRO FECHA
    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    rango_fecha = st.sidebar.date_input(
        "Rango de Fecha",
        [fecha_min, fecha_max]
    )

    # FILTRO PRODUCTO
    if "Producto" in df.columns:
        productos = st.sidebar.multiselect(
            "Producto",
            df["Producto"].unique(),
            default=df["Producto"].unique()
        )
    else:
        productos = None

    # FILTRO CLIENTE
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
        df.groupby("Periodo")[["Ventas", "Costos", "Ganancia"]]
        .sum()
        .reset_index()
    )

    df_group = df_group.sort_values("Periodo")

    # -------------------------
    # KPIs
    # -------------------------
    st.subheader("📊 KPIs Ejecutivos")

    ventas_total = df["Ventas"].sum()
    costos_total = df["Costos"].sum()
    ganancia_total = df["Ganancia"].sum()

    margen = 0 if ventas_total == 0 else (ganancia_total / ventas_total) * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Ventas", round(ventas_total, 0))
    col2.metric("📈 Ganancia", round(ganancia_total, 0))
    col3.metric("💸 Costos", round(costos_total, 0))
    col4.metric("📊 Margen %", round(margen, 1))

    # -------------------------
    # INSIGHTS
    # -------------------------
    st.markdown("---")
    st.subheader("🧠 Insights")

    if not df_group.empty:
        mejor = df_group.loc[df_group["Ventas"].idxmax()]
        peor = df_group.loc[df_group["Ventas"].idxmin()]

        st.success(f"Mejor periodo: {mejor['Periodo']} → {round(mejor['Ventas'],0)}")
        st.warning(f"Peor periodo: {peor['Periodo']} → {round(peor['Ventas'],0)}")

    # -------------------------
    # ANÁLISIS VISUAL
    # -------------------------
    st.markdown("---")
    st.subheader("📈 Análisis Visual")

    if vista == "Ventas":
        y_data = ["Ventas"]
    elif vista == "Ganancia":
        y_data = ["Ganancia"]
    else:
        y_data = ["Ventas", "Ganancia"]

    if tipo == "Línea":
        fig = px.line(df_group, x="Periodo", y=y_data, markers=True)
    else:
        fig = px.area(df_group, x="Periodo", y=y_data)

    fig.update_layout(
        hovermode="x unified",
        transition_duration=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # EVOLUCIÓN ANIMADA (LÍNEA)
    # -------------------------
    st.markdown("---")
    st.subheader("▶️ Evolución dinámica")

    fig_anim = px.line(
        df_group,
        x="Periodo",
        y=["Ventas", "Ganancia"],
        markers=True,
        animation_frame="Periodo"
    )

    fig_anim.update_layout(hovermode="x unified")

    st.plotly_chart(fig_anim, use_container_width=True)

    # -------------------------
    # PRODUCTO
    # -------------------------
    if "Producto" in df.columns:
        st.markdown("---")
        st.subheader("📦 Ventas por Producto")

        ventas_prod = (
            df.groupby("Producto")["Ventas"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_prod = px.bar(
            ventas_prod,
            x="Producto",
            y="Ventas",
            color="Ventas"
        )

        st.plotly_chart(fig_prod, use_container_width=True)

    # -------------------------
    # CLIENTES
    # -------------------------
    if "Nombre" in df.columns:
        st.markdown("---")
        st.subheader("👤 Ventas por Cliente")

        ventas_cliente = (
            df.groupby("Nombre")["Ventas"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig_cli = px.bar(
            ventas_cliente,
            x="Nombre",
            y="Ventas",
            color="Ventas"
        )

        st.plotly_chart(fig_cli, use_container_width=True)

    # -------------------------
    # DATOS
    # -------------------------
    st.markdown("---")

    with st.expander("📂 Ver datos"):
        st.dataframe(df)

else:
    st.info("📂 Sube un archivo Excel para comenzar")
