import streamlit as st
from ui_components import card_kpi
import plotly.express as px
proximos_agotarse_app
detalle_criticos_app
# =========================
# KPI CRÍTICOS
# =========================
def kpi_criticos(df):

    criticos = df[
        df["STOCK"] < df["STOCK_MIN"]
    ]

    card_kpi(
        "🚨 Productos Críticos",
        len(criticos)
    )


# =========================
# GRÁFICA CRÍTICOS
# =========================
def grafica_criticos(df):

    criticos = df[df["STOCK"] < df["STOCK_MIN"]]

    if criticos.empty:
        st.success("✅ No hay productos críticos en este momento")
        return

    top = criticos.sort_values("STOCK").head(10)

    st.subheader("📉 Top 10 Productos Más Críticos")

    fig = px.bar(
        top,
        x="STOCK",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="STOCK",
        hover_data=[
            "NUMERO_PRODUCTO",
            "STOCK_MIN",
            "SALIDA"
        ],
        title="Productos con menor stock disponible"
    )

    fig.update_layout(
        height=480,
        yaxis_title="Producto",
        xaxis_title="Stock actual",
        title_x=0.02,
        margin=dict(l=10, r=10, t=60, b=10)
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
# =========================
# TABLA CRÍTICOS
# =========================
def tabla_criticos(df):

    criticos = df[
        df["STOCK"] < df["STOCK_MIN"]
    ]

    st.subheader("📋 Detalle Productos Críticos")

    st.dataframe(
        criticos[
            [
                "NUMERO_PRODUCTO",
                "NOMBRE_PRODUCTO",
                "STOCK",
                "STOCK_MIN",
                "SALIDA"
            ]
        ]
    )


# =========================
# DASHBOARD CRÍTICOS
# =========================
def dashboard_criticos(df):

    st.title("🚨 Dashboard Críticos")

    kpi_criticos(df)

    grafica_criticos(df)

    tabla_criticos(df)
def sin_stock_app(df):

    st.subheader("❌ Productos Sin Stock")

    sin_stock = df[df["STOCK"] <= 0]

    card_kpi("❌ Total Sin Stock", len(sin_stock), "#c0392b")

    if sin_stock.empty:
        st.success("✅ No hay productos sin stock")
        return

    st.markdown("### 📉 Productos agotados")

    fig = px.bar(
        sin_stock.head(10),
        x="NOMBRE_PRODUCTO",
        y="STOCK",
        text="STOCK",
        title="Top productos sin stock"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Detalle sin stock")
    st.dataframe(sin_stock, use_container_width=True)


def riesgo_alto_app(df):

    st.subheader("🔥 Productos en Riesgo Alto")

    riesgo_alto = df[
        df["STOCK"] <= (df["STOCK_MIN"] * 0.5)
    ]

    card_kpi("🔥 Total Riesgo Alto", len(riesgo_alto), "#e67e22")

    if riesgo_alto.empty:
        st.success("✅ No hay productos en riesgo alto")
        return

    top = riesgo_alto.sort_values("STOCK").head(10)

    st.markdown("### 📉 Top riesgo alto")

    fig = px.bar(
        top,
        x="STOCK",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="STOCK",
        title="Productos con stock más bajo vs mínimo"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Detalle riesgo alto")
    st.dataframe(riesgo_alto, use_container_width=True)


def proximos_agotarse_app(df):

    st.subheader("⚠️ Productos Próximos a Agotarse")

    proximos = df[
        (df["STOCK"] > df["STOCK_MIN"]) &
        (df["STOCK"] <= (df["STOCK_MIN"] * 1.2))
    ]

    card_kpi("⚠️ Total Próximos", len(proximos), "#f1c40f")

    if proximos.empty:
        st.success("✅ No hay productos próximos a agotarse")
        return

    top = proximos.sort_values("STOCK").head(10)

    st.markdown("### 📉 Próximos a agotarse")

    fig = px.bar(
        top,
        x="STOCK",
        y="NOMBRE_PRODUCTO",
        orientation="h",
        text="STOCK",
        title="Productos cerca del mínimo"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Detalle próximos a agotarse")
    st.dataframe(proximos, use_container_width=True)


def detalle_criticos_app(df):

    st.subheader("📋 Detalle General Críticos")

    criticos = df[df["STOCK"] < df["STOCK_MIN"]]

    card_kpi("🚨 Total Críticos", len(criticos), "#e74c3c")

    if criticos.empty:
        st.success("✅ No hay productos críticos")
        return

    st.markdown("### 📊 Comparativo Stock vs Mínimo")

    top = criticos.sort_values("STOCK").head(15)

    fig = px.bar(
        top,
        x="NOMBRE_PRODUCTO",
        y=["STOCK", "STOCK_MIN"],
        barmode="group",
        title="Stock actual vs stock mínimo"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Tabla completa críticos")
    st.dataframe(criticos, use_container_width=True)
