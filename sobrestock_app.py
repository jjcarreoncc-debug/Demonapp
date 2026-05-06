import streamlit as st
import plotly.express as px
from ui_components import card_kpi


def dashboard_sobrestock(df):

    st.subheader("⚠️ Dashboard Sobrestock")
    st.write(df[["STOCK", "STOCK_MAX"]].head())

    sobrestock = df[df["STOCK"] > df["STOCK_MAX"]]

    exceso_total = (
        sobrestock["STOCK"] - sobrestock["STOCK_MAX"]
    ).sum()

    porcentaje = round(
        (len(sobrestock) / len(df)) * 100,
        1
    ) if len(df) > 0 else 0

    c1, c2, c3 = st.columns(3)

    with c1:
        card_kpi("⚠️ Productos Sobrestock", len(sobrestock), "#f39c12")

    with c2:
        card_kpi("📦 Exceso Total", int(exceso_total), "#e67e22")

    with c3:
        card_kpi("📊 % Sobrestock", f"{porcentaje}%", "#8e44ad")

    if sobrestock.empty:
        st.success("✅ No hay productos con sobrestock")
        return

    st.markdown("### 📊 Top productos con mayor exceso")

    sobrestock = sobrestock.copy()
    sobrestock["EXCESO"] = sobrestock["STOCK"] - sobrestock["STOCK_MAX"]

    top = sobrestock.sort_values("EXCESO", ascending=False).head(10)

    fig = px.bar(
        top,
        x="EXCESO",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="EXCESO",
        title="Productos con mayor exceso de inventario"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Detalle Sobrestock")
    st.dataframe(sobrestock, use_container_width=True)


def mayor_exceso_app(df):

    st.subheader("📦 Mayor Exceso")

    sobrestock = df[df["STOCK"] > df["STOCK_MAX"]].copy()

    if sobrestock.empty:
        st.success("✅ No hay exceso de inventario")
        return

    sobrestock["EXCESO"] = sobrestock["STOCK"] - sobrestock["STOCK_MAX"]

    total_exceso = int(sobrestock["EXCESO"].sum())

    card_kpi("📦 Exceso Total", total_exceso, "#e67e22")

    top = sobrestock.sort_values("EXCESO", ascending=False).head(15)

    fig = px.bar(
        top,
        x="NOMBRE_PRODUCTO",
        y="EXCESO",
        text="EXCESO",
        title="Exceso por producto"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(top, use_container_width=True)


def capital_detenido_app(df):

    st.subheader("💰 Capital Detenido")

    sobrestock = df[df["STOCK"] > df["STOCK_MAX"]].copy()

    if sobrestock.empty:
        st.success("✅ No hay capital detenido por sobrestock")
        return

    sobrestock["EXCESO"] = sobrestock["STOCK"] - sobrestock["STOCK_MAX"]

    if "PRECIO" in sobrestock.columns:
        sobrestock["CAPITAL_DETENIDO"] = sobrestock["EXCESO"] * sobrestock["PRECIO"]
    else:
        sobrestock["CAPITAL_DETENIDO"] = sobrestock["EXCESO"]

    total_capital = sobrestock["CAPITAL_DETENIDO"].sum()

    card_kpi("💰 Capital Detenido", f"${total_capital:,.0f}", "#27ae60")

    top = sobrestock.sort_values(
        "CAPITAL_DETENIDO",
        ascending=False
    ).head(10)

    fig = px.bar(
        top,
        x="CAPITAL_DETENIDO",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="CAPITAL_DETENIDO",
        title="Capital detenido por producto"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(top, use_container_width=True)


def detalle_sobrestock_app(df):

    st.subheader("📋 Detalle General Sobrestock")

    sobrestock = df[df["STOCK"] > df["STOCK_MAX"]].copy()

    if sobrestock.empty:
        st.success("✅ No hay productos con sobrestock")
        return

    sobrestock["EXCESO"] = sobrestock["STOCK"] - sobrestock["STOCK_MAX"]

    card_kpi("⚠️ Total Sobrestock", len(sobrestock), "#f39c12")

    st.dataframe(sobrestock, use_container_width=True)
