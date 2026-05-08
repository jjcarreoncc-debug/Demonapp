import streamlit as st
import pandas as pd
import plotly.express as px


# =========================
# KPI CARD
# =========================
def card_kpi(titulo, valor, color):

    st.markdown(
        f"""
        <div style="
            background:{color};
            padding:20px;
            border-radius:14px;
            color:white;
            text-align:center;
            margin-bottom:15px;
        ">
            <h4>{titulo}</h4>
            <h2>{valor}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# DASHBOARD GENERAL
# =========================
def dashboard_compras_general(df):

    st.subheader("📥 Dashboard Compras")

    if "ENTRADA" not in df.columns:
        st.warning("No existe la columna ENTRADA")
        return

    df["ENTRADA"] = pd.to_numeric(
        df["ENTRADA"],
        errors="coerce"
    ).fillna(0)

    compras_total = int(df["ENTRADA"].sum())

    productos_comprados = df[
        df["ENTRADA"] > 0
    ].shape[0]

    numero_compras = productos_comprados

    if "PRECIO_COMPRA" in df.columns:

        df["PRECIO_COMPRA"] = pd.to_numeric(
            df["PRECIO_COMPRA"],
            errors="coerce"
        )

        df["VALOR_COMPRADO"] = (
            df["ENTRADA"]
            * df["PRECIO_COMPRA"]
        )

        valor_comprado = df[
            "VALOR_COMPRADO"
        ].sum()

        compras_sin_precio = df[
            (df["ENTRADA"] > 0)
            & (df["PRECIO_COMPRA"].isna())
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
        card_kpi(
            "📥 Compras Totales",
            compras_total,
            "#2980b9"
        )

    with c2:
        card_kpi(
            "💰 Valor Comprado",
            f"${valor_comprado:,.0f}",
            "#27ae60"
        )

    with c3:
        card_kpi(
            "📦 Productos Comprados",
            productos_comprados,
            "#8e44ad"
        )

    with c4:
        card_kpi(
            "📊 Promedio Compra",
            f"${promedio_compra:,.0f}",
            "#f39c12"
        )

    c5, c6 = st.columns(2)

    with c5:
        card_kpi(
            "🧾 Número Compras",
            numero_compras,
            "#34495e"
        )

    with c6:
        card_kpi(
            "⚠️ Sin Precio",
            compras_sin_precio,
            "#c0392b"
        )

    compras = df[
        df["ENTRADA"] > 0
    ].copy()

    if compras.empty:
        st.success("✅ No hay compras registradas")
        return

    if "NOMBRE_PRODUCTO" in compras.columns:

        st.markdown("### 🏆 Top productos comprados")

        top = (
            compras
            .sort_values(
                "ENTRADA",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            top,
            x="ENTRADA",
            y="NOMBRE_PRODUCTO",
            orientation="h",
            text="ENTRADA",
            title="Productos más comprados",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="top_productos_dashboard"
        )

    st.markdown("### 📋 Detalle compras")

    st.dataframe(
        compras,
        use_container_width=True
    )


# =========================
# TOP COMPRAS
# =========================
def top_compras_app(df):

    st.subheader("🏆 Top Compras")

    if "ENTRADA" not in df.columns:
        st.warning("No existe la columna ENTRADA")
        return

    compras = df[
        df["ENTRADA"] > 0
    ].copy()

    if compras.empty:
        st.success("✅ No hay compras registradas")
        return

    if "NOMBRE_PRODUCTO" not in compras.columns:
        st.warning("No existe NOMBRE_PRODUCTO")
        return

    top = (
        compras
        .sort_values(
            "ENTRADA",
            ascending=False
        )
        .head(15)
    )

    card_kpi(
        "🏆 Producto Más Comprado",
        top.iloc[0]["NOMBRE_PRODUCTO"],
        "#8e44ad"
    )

    fig = px.bar(
        top,
        x="ENTRADA",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="ENTRADA",
        title="Ranking productos comprados",
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="ranking_top_compras"
    )

    st.dataframe(
        top,
        use_container_width=True
    )


# =========================
# COSTOS
# =========================
def costos_compras_app(df):

    st.subheader("💰 Costos Compras")

    if (
        "PRECIO_COMPRA" not in df.columns
        or "ENTRADA" not in df.columns
    ):
        st.warning(
            "No existen columnas de costos."
        )
        return

    compras = df[
        df["ENTRADA"] > 0
    ].copy()

    compras["PRECIO_COMPRA"] = pd.to_numeric(
        compras["PRECIO_COMPRA"],
        errors="coerce"
    )

    compras["VALOR_COMPRADO"] = (
        compras["ENTRADA"]
        * compras["PRECIO_COMPRA"]
    )

    total = compras[
        "VALOR_COMPRADO"
    ].sum()

    card_kpi(
        "💰 Valor Comprado Total",
        f"${total:,.0f}",
        "#27ae60"
    )

    if "NOMBRE_PRODUCTO" in compras.columns:

        top = (
            compras
            .sort_values(
                "VALOR_COMPRADO",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            top,
            x="VALOR_COMPRADO",
            y="NOMBRE_PRODUCTO",
            orientation="h",
            text="VALOR_COMPRADO",
            title="Productos mayor valor comprado",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="costos_productos"
        )

    st.dataframe(
        compras,
        use_container_width=True
    )


# =========================
# SIN PRECIO
# =========================
def compras_sin_precio_app(df):

    st.subheader("⚠️ Compras Sin Precio")

    if (
        "PRECIO_COMPRA" not in df.columns
        or "ENTRADA" not in df.columns
    ):
        st.warning(
            "No existe PRECIO_COMPRA."
        )
        return

    sin_precio = df[
        (df["ENTRADA"] > 0)
        & (df["PRECIO_COMPRA"].isna())
    ]

    card_kpi(
        "⚠️ Compras Sin Precio",
        len(sin_precio),
        "#c0392b"
    )

    if sin_precio.empty:
        st.success("✅ Todas las compras tienen precio")
        return

    st.dataframe(
        sin_precio,
        use_container_width=True
    )


# =========================
# DETALLE
# =========================
def detalle_compras_app(df):

    st.subheader("📋 Detalle Compras")

    if "ENTRADA" in df.columns:

        compras = df[
            df["ENTRADA"] > 0
        ].copy()

    else:

        compras = df.copy()

    card_kpi(
        "📥 Registros Compra",
        len(compras),
        "#2980b9"
    )

    st.dataframe(
        compras,
        use_container_width=True
    )
