import streamlit as st

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

def sin_stock_app(df):

    st.subheader("❌ Productos Sin Stock")

    sin_stock = df[
        df["STOCK"] <= 0
    ]

    st.metric("❌ Total Sin Stock", len(sin_stock))

    st.dataframe(sin_stock)


def riesgo_alto_app(df):

    st.subheader("🔥 Productos en Riesgo Alto")

    riesgo_alto = df[
        df["STOCK"] <= (df["STOCK_MIN"] * 0.5)
    ]

    st.metric("🔥 Total Riesgo Alto", len(riesgo_alto))

    st.dataframe(riesgo_alto)


def proximos_agotarse_app(df):

    st.subheader("⚠️ Productos Próximos a Agotarse")

    proximos = df[
        (df["STOCK"] > df["STOCK_MIN"]) &
        (df["STOCK"] <= (df["STOCK_MIN"] * 1.2))
    ]

    st.metric("⚠️ Total Próximos a Agotarse", len(proximos))

    st.dataframe(proximos)


def detalle_criticos_app(df):

    st.subheader("📋 Detalle General Críticos")

    criticos = df[
        df["STOCK"] < df["STOCK_MIN"]
    ]

    st.dataframe(criticos)
