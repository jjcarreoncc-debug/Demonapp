import streamlit as st
import pandas as pd
import plotly.express as px

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


def grafica_barra(df, x, y, titulo, orientacion="v", color="#1f77b4"):

    if df is None or df.empty:
        st.info("No hay datos para graficar.")
        return

    fig = px.bar(
        df,
        x=x,
        y=y,
        orientation=orientacion,
        text=x if orientacion == "h" else y,
        title=titulo,
        template="plotly_white"
    )

    fig.update_traces(
        marker_color=color,
        textposition="outside"
    )

    fig.update_layout(
        height=430,
        margin=dict(l=30, r=30, t=60, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)


def compras_analitica_app(df):

    st.title("📈 Analítica de Compras")

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    if "ENTRADA" not in df.columns:
        st.warning("No existe la columna ENTRADA.")
        return

    df["ENTRADA"] = pd.to_numeric(
        df["ENTRADA"],
        errors="coerce"
    ).fillna(0)

    if "PRECIO_COMPRA" in df.columns:
        df["PRECIO_COMPRA"] = pd.to_numeric(
            df["PRECIO_COMPRA"],
            errors="coerce"
        )

        df["VALOR_COMPRADO"] = (
            df["ENTRADA"] * df["PRECIO_COMPRA"]
        )
    else:
        df["PRECIO_COMPRA"] = 0
        df["VALOR_COMPRADO"] = 0

    compras = df[df["ENTRADA"] > 0].copy()

    if compras.empty:
        st.success("No hay compras para analizar.")
        return

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Tendencias",
        "💰 Costos",
        "🏆 Rankings",
        "⚠️ Riesgos"
    ])

    # =========================
    # TAB 1 - TENDENCIAS
    # =========================
    with tab1:

        st.subheader("📈 Tendencias de compras")

        fecha_col = None

        for col in [
            "FECHA_COMPRA",
            "FECHA",
            "FECHA_DOCUMENTO",
            "FECHA_ORDEN"
        ]:
            if col in compras.columns:
                fecha_col = col
                break

        if fecha_col is not None:

            compras[fecha_col] = pd.to_datetime(
                compras[fecha_col],
                errors="coerce"
            )

            tendencia = (
                compras
                .dropna(subset=[fecha_col])
                .groupby(
                    compras[fecha_col]
                    .dt.to_period("M")
                    .astype(str)
                )
                .agg({
                    "ENTRADA": "sum",
                    "VALOR_COMPRADO": "sum"
                })
                .reset_index()
            )

            tendencia.columns = [
                "Mes",
                "Unidades Compradas",
                "Valor Comprado"
            ]

            c1, c2 = st.columns(2)

            with c1:
                fig = px.line(
                    tendencia,
                    x="Mes",
                    y="Unidades Compradas",
                    markers=True,
                    title="Unidades compradas por mes",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                fig = px.line(
                    tendencia,
                    x="Mes",
                    y="Valor Comprado",
                    markers=True,
                    title="Valor comprado por mes",
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(tendencia, use_container_width=True)

        else:
            st.warning("No se encontró columna de fecha para tendencias.")

    # =========================
    # TAB 2 - COSTOS
    # =========================
    with tab2:

        st.subheader("💰 Análisis de costos")

        valor_total = compras["VALOR_COMPRADO"].sum()
        costo_promedio = compras["PRECIO_COMPRA"].mean()
        registros_sin_precio = compras[
            compras["PRECIO_COMPRA"].isna()
        ].shape[0]

        c1, c2, c3 = st.columns(3)

        with c1:
            card_kpi(
                "💰 Valor comprado",
                f"${valor_total:,.0f}",
                "#27ae60"
            )

        with c2:
            card_kpi(
                "📊 Costo promedio",
                f"${costo_promedio:,.0f}",
                "#2980b9"
            )

        with c3:
            card_kpi(
                "⚠️ Sin precio",
                registros_sin_precio,
                "#c0392b"
            )

        if "NOMBRE_PRODUCTO" in compras.columns:

            top_valor = (
                compras
                .groupby("NOMBRE_PRODUCTO")["VALOR_COMPRADO"]
                .sum()
                .reset_index()
                .sort_values("VALOR_COMPRADO", ascending=False)
                .head(10)
            )

            grafica_barra(
                top_valor,
                "VALOR_COMPRADO",
                "NOMBRE_PRODUCTO",
                "Productos con mayor valor comprado",
                "h",
                "#27ae60"
            )

        if "NOMBRE_PROVEEDOR" in compras.columns:

            proveedor_valor = (
                compras
                .groupby("NOMBRE_PROVEEDOR")["VALOR_COMPRADO"]
                .sum()
                .reset_index()
                .sort_values("VALOR_COMPRADO", ascending=False)
                .head(10)
            )

            grafica_barra(
                proveedor_valor,
                "VALOR_COMPRADO",
                "NOMBRE_PROVEEDOR",
                "Proveedores con mayor valor comprado",
                "h",
                "#8e44ad"
            )

    # =========================
    # TAB 3 - RANKINGS
    # =========================
    with tab3:

        st.subheader("🏆 Rankings de compras")

        if "NOMBRE_PRODUCTO" in compras.columns:

            top_productos = (
                compras
                .groupby("NOMBRE_PRODUCTO")["ENTRADA"]
                .sum()
                .reset_index()
                .sort_values("ENTRADA", ascending=False)
                .head(15)
            )

            grafica_barra(
                top_productos,
                "ENTRADA",
                "NOMBRE_PRODUCTO",
                "Top productos comprados",
                "h",
                "#1f77b4"
            )

        if "NOMBRE_PROVEEDOR" in compras.columns:

            top_proveedores = (
                compras
                .groupby("NOMBRE_PROVEEDOR")["ENTRADA"]
                .sum()
                .reset_index()
                .sort_values("ENTRADA", ascending=False)
                .head(15)
            )

            grafica_barra(
                top_proveedores,
                "ENTRADA",
                "NOMBRE_PROVEEDOR",
                "Top proveedores por unidades compradas",
                "h",
                "#f39c12"
            )

        if "NOMBRE_BODEGA" in compras.columns:

            top_bodegas = (
                compras
                .groupby("NOMBRE_BODEGA")["ENTRADA"]
                .sum()
                .reset_index()
                .sort_values("ENTRADA", ascending=False)
                .head(15)
            )

            grafica_barra(
                top_bodegas,
                "ENTRADA",
                "NOMBRE_BODEGA",
                "Top bodegas por compras recibidas",
                "h",
                "#16a085"
            )

    # =========================
    # TAB 4 - RIESGOS
    # =========================
    with tab4:

        st.subheader("⚠️ Riesgos de compras")

        sin_precio = compras[
            compras["PRECIO_COMPRA"].isna()
        ]

        compras_altas = compras[
            compras["VALOR_COMPRADO"]
            > compras["VALOR_COMPRADO"].quantile(0.90)
        ]

        c1, c2 = st.columns(2)

        with c1:
            card_kpi(
                "⚠️ Compras sin precio",
                len(sin_precio),
                "#c0392b"
            )

        with c2:
            card_kpi(
                "🚨 Compras valor alto",
                len(compras_altas),
                "#e67e22"
            )

        st.markdown("### ⚠️ Compras sin precio")
        st.dataframe(sin_precio, use_container_width=True)

        st.markdown("### 🚨 Compras con valor alto")
        st.dataframe(compras_altas, use_container_width=True)
