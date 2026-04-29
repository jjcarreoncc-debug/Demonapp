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
# CARGA DE ARCHIVO
# -------------------------
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)

    # -------------------------
    # LIMPIEZA
    # -------------------------
    df.columns = df.columns.str.strip()

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha"])

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

    # -------------------------
    # KPIs EJECUTIVOS
    # -------------------------
    st.subheader("📊 KPIs Ejecutivos")

    ventas_total = df_group["Ventas"].sum()
    costos_total = df_group["Costos"].sum()
    ganancia_total = df_group["Ganancia"].sum()

    # Previos
    df_group["Ventas_prev"] = df_group["Ventas"].shift(1)
    df_group["Ganancia_prev"] = df_group["Ganancia"].shift(1)

    ventas_prev = df_group["Ventas_prev"].sum()
    ganancia_prev = df_group["Ganancia_prev"].sum()

    delta_ventas = ventas_total - ventas_prev
    delta_ganancia = ganancia_total - ganancia_prev

    margen = 0 if ventas_total == 0 else (ganancia_total / ventas_total) * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Ventas", round(ventas_total, 0), round(delta_ventas, 0))
    col2.metric("📈 Ganancia", round(ganancia_total, 0), round(delta_ganancia, 0))
    col3.metric("💸 Costos", round(costos_total, 0))
    col4.metric("📊 Margen %", round(margen, 1))

    # -------------------------
    # MENSAJES EJECUTIVOS
    # -------------------------
    if delta_ganancia > 0:
        st.success("📈 El negocio está creciendo en ganancias")
    else:
        st.error("📉 Las ganancias están disminuyendo")

    if margen > 20:
        st.info("💡 Buen margen de rentabilidad")
    elif margen > 0:
        st.warning("⚠️ Margen bajo, revisar costos")
    else:
        st.error("🚨 Negocio en pérdida")

    # -------------------------
    # INSIGHTS
    # -------------------------
    st.markdown("---")
    st.subheader("🧠 Insights automáticos")

    mejor = df_group.loc[df_group["Ventas"].idxmax()]
    peor = df_group.loc[df_group["Ventas"].idxmin()]

    st.success(f"📈 Mejor periodo: {mejor['Periodo']} → {round(mejor['Ventas'],0)}")
    st.warning(f"📉 Peor periodo: {peor['Periodo']} → {round(peor['Ventas'],0)}")

    # -------------------------
    # ANALISIS VISUAL
    # -------------------------
    fig = px.line(
    df_group,
    x="Periodo",
    y=["Ventas", "Ganancia"],
    markers=True,
    title="Tendencia de Ventas y Ganancia"
)

st.plotly_chart(fig, use_container_width=True)
 
fig_bar = px.bar(
    df_group,
    x="Periodo",
    y="Ventas",
    title="Ventas por Periodo",
    text_auto=True
)

st.plotly_chart(fig_bar, use_container_width=True)

fig = px.line(
    df_group,
    x="Periodo",
    y=["Ventas", "Ganancia"],
    markers=True,
    color_discrete_sequence=["#60A5FA", "#34D399"]
)
    # -------------------------
    # RENTABILIDAD
    # -------------------------
st.markdown("---")
st.subheader("💰 Rentabilidad")

df_group["Margen %"] = df_group.apply(
    lambda x: (x["Ganancia"] / x["Ventas"] * 100) if x["Ventas"] != 0 else 0,
    axis=1
)
st.line_chart(df_group.set_index("Periodo")["Margen %"])

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
    )

 st.bar_chart(ventas_prod)

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
        )

        st.bar_chart(ventas_cliente)

        st.subheader("🏆 Top Clientes")

        top_clientes = ventas_cliente.head(5)
        st.dataframe(top_clientes)

    # -------------------------
    # CLIENTE + PRODUCTO
    # -------------------------
    if "Nombre" in df.columns and "Producto" in df.columns:
        st.markdown("---")
        st.subheader("🏆 Cliente + Producto")

        top_combo = (
            df.groupby(["Nombre", "Producto"])["Ventas"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )

        st.dataframe(top_combo)

    # -------------------------
    # DATOS
    # -------------------------
    st.markdown("---")

    with st.expander("📂 Ver datos completos"):
        st.dataframe(df)

else:
    st.info("📂 Sube un archivo Excel para comenzar")
