import streamlit as st
from ui_components import card_kpi
import plotly.express as px
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

    sin_stock = df[
        df["STOCK"] <= 0
    ]

    card_kpi("❌ Total Sin Stock", len(sin_stock))

    st.dataframe(sin_stock)


def riesgo_alto_app(df):

    st.subheader("🔥 Productos en Riesgo Alto")

    riesgo_alto = df[
        df["STOCK"] <= (df["STOCK_MIN"] * 0.5)
    ]

    card_kpi("🔥 Total Riesgo Alto", len(riesgo_alto))

    st.dataframe(riesgo_alto)


def proximos_agotarse_app(df):

    st.subheader("⚠️ Productos Próximos a Agotarse")

    proximos = df[
        (df["STOCK"] > df["STOCK_MIN"]) &
        (df["STOCK"] <= (df["STOCK_MIN"] * 1.2))
    ]

    card_kpi("⚠️ Total Próximos a Agotarse", len(proximos))

    st.dataframe(proximos)


def detalle_criticos_app(df):

    st.subheader("📋 Detalle General Críticos")

    criticos = df[
        df["STOCK"] < df["STOCK_MIN"]
    ]

    st.dataframe(criticos)
def sin_stock_app(df):

    st.subheader("❌ Productos Sin Stock")

    sin_stock = df[df["STOCK"] <= 0]

    card_kpi("❌ Total Sin Stock", len(sin_stock))

    st.dataframe(sin_stock)


def riesgo_alto_app(df):

    st.subheader("🔥 Productos en Riesgo Alto")

    riesgo_alto = df[
        df["STOCK"] <= (df["STOCK_MIN"] * 0.5)
    ]

    card_kpi("🔥 Total Riesgo Alto", len(riesgo_alto))

    st.dataframe(riesgo_alto)


def proximos_agotarse_app(df):

    st.subheader("⚠️ Productos Próximos a Agotarse")

    proximos = df[
        (df["STOCK"] > df["STOCK_MIN"]) &
        (df["STOCK"] <= (df["STOCK_MIN"] * 1.2))
    ]

    card_kpi("⚠️ Total Próximos a Agotarse", len(proximos))

    st.dataframe(proximos)


def detalle_criticos_app(df):

    st.subheader("📋 Detalle General Críticos")

    criticos = df[df["STOCK"] < df["STOCK_MIN"]]

    card_kpi("🚨 Total Críticos", len(criticos))

    st.dataframe(criticos)
