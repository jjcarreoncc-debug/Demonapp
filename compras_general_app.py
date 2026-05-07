import streamlit as st
import plotly.express as px
from ui_components import card_kpi


def dashboard_compras_general(df):

    st.subheader("📥 Dashboard Compras")

    compras_total = int(df["ENTRADA"].sum())
    productos_comprados = df[df["ENTRADA"] > 0].shape[0]
    numero_compras = df[df["ENTRADA"] > 0].shape[0]

    if "PRECIO_COMPRA" in df.columns:
        df["VALOR_COMPRADO"] = df["ENTRADA"] * df["PRECIO_COMPRA"]
        valor_comprado = df["VALOR_COMPRADO"].sum()
        compras_sin_precio = df[
            (df["ENTRADA"] > 0) &
            (df["PRECIO_COMPRA"].isna())
        ].shape[0]
    else:
        df["VALOR_COMPRADO"] = 0
        valor_comprado = 0
        compras_sin_precio = 0

    promedio_compra = (
        valor_comprado / numero_compras
        if numero_compras > 0
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        card_kpi("📥 Compras Totales", compras_total, "#2980b9")

    with c2:
        card_kpi("💰 Valor Comprado", f"${valor_comprado:,.0f}", "#27ae60")

    with c3:
        card_kpi("📦 Productos Comprados", productos_comprados, "#8e44ad")

    with c4:
        card_kpi("📊 Promedio Compra", f"${promedio_compra:,.0f}", "#f39c12")

    c5, c6 = st.columns(2)

    with c5:
        card_kpi("🧾 Número de Compras", numero_compras, "#34495e")

    with c6:
        card_kpi("⚠️ Compras Sin Precio", compras_sin_precio, "#c0392b")

    compras = df[df["ENTRADA"] > 0].copy()

    if compras.empty:
        st.success("✅ No hay compras registradas")
        return

    st.markdown("### 🏆 Top productos comprados")

    top = compras.sort_values("ENTRADA", ascending=False).head(10)

    fig = px.bar(
        top,
        x="ENTRADA",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="ENTRADA",
        title="Productos más comprados"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Detalle compras")
    st.dataframe(compras, use_container_width=True)


def top_compras_app(df):

    st.subheader("🏆 Top Compras")

    compras = df[df["ENTRADA"] > 0].copy()

    if compras.empty:
        st.success("✅ No hay compras registradas")
        return

    top = compras.sort_values("ENTRADA", ascending=False).head(15)

    card_kpi("🏆 Producto Más Comprado", top.iloc[0]["NOMBRE_PRODUCTO"], "#8e44ad")

    fig = px.bar(
        top,
        x="ENTRADA",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="ENTRADA",
        title="Ranking de productos comprados"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(top, use_container_width=True)


def costos_compras_app(df):

    st.subheader("💰 Costos de Compras")

    compras = df[df["ENTRADA"] > 0].copy()

    if "PRECIO_COMPRA" not in compras.columns:
        st.warning("⚠️ No existe la columna PRECIO_COMPRA")
        return

    compras["VALOR_COMPRADO"] = compras["ENTRADA"] * compras["PRECIO_COMPRA"]

    total = compras["VALOR_COMPRADO"].sum()

    card_kpi("💰 Valor Comprado Total", f"${total:,.0f}", "#27ae60")

    top = compras.sort_values("VALOR_COMPRADO", ascending=False).head(10)

    fig = px.bar(
        top,
        x="VALOR_COMPRADO",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="VALOR_COMPRADO",
        title="Productos con mayor valor comprado"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(top, use_container_width=True)


def compras_sin_precio_app(df):

    st.subheader("⚠️ Compras Sin Precio")

    if "PRECIO_COMPRA" not in df.columns:
        st.warning("⚠️ No existe la columna PRECIO_COMPRA")
        return

    sin_precio = df[
        (df["ENTRADA"] > 0) &
        (df["PRECIO_COMPRA"].isna())
    ]

    card_kpi("⚠️ Compras Sin Precio", len(sin_precio), "#c0392b")

    if sin_precio.empty:
        st.success("✅ Todas las compras tienen precio")
        return

    st.dataframe(sin_precio, use_container_width=True)


def detalle_compras_app(df):

    st.subheader("📋 Detalle General Compras")

    compras = df[df["ENTRADA"] > 0].copy()

    card_kpi("📥 Registros de Compra", len(compras), "#2980b9")

    st.dataframe(compras, use_container_width=True)
