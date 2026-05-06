
import streamlit as st
def alertas_app():

    # =========================
# KPI CRÍTICOS
# =========================
def kpi_criticos(df):

    criticos = df[
        df["STOCK"] < df["STOCK_MIN"]
    ]

    st.metric(
        "🚨 Productos Críticos",
        len(criticos)
    )


# =========================
# GRÁFICA CRÍTICOS
# =========================
def grafica_criticos(df):

    criticos = df[
        df["STOCK"] < df["STOCK_MIN"]
    ]

    top = criticos.sort_values(
        "STOCK"
    ).head(10)

    st.subheader("📉 Productos Más Críticos")

    st.bar_chart(
        top.set_index(
            "NOMBRE_PRODUCTO"
        )["STOCK"]
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
