import streamlit as st
import plotly.express as px
from ui_components import card_kpi


# =========================
# DASHBOARD ROTACIÓN
# =========================
def dashboard_rotacion(df):

    st.subheader("🔄 Dashboard Rotación")

    top_vendidos = df.sort_values(
        "SALIDA",
        ascending=False
    )

    baja_rotacion = df[
        df["SALIDA"] <= 5
    ]

    rotacion_promedio = round(
        df["SALIDA"].mean(),
        2
    )

    salida_total = int(df["SALIDA"].sum())

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        card_kpi(
            "📦 Salida Total",
            salida_total,
            "#3498db"
        )

    with c2:
        card_kpi(
            "🔥 Top Vendidos",
            len(top_vendidos.head(10)),
            "#e74c3c"
        )

    with c3:
        card_kpi(
            "🐢 Baja Rotación",
            len(baja_rotacion),
            "#f39c12"
        )

    with c4:
        card_kpi(
            "📈 Rotación Promedio",
            rotacion_promedio,
            "#2ecc71"
        )

    st.markdown("### 📊 Top productos vendidos")

    fig = px.bar(
        top_vendidos.head(10),
        x="NOMBRE_PRODUCTO",
        y="SALIDA",
        text="SALIDA",
        title="Top 10 productos más vendidos"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================
# TOP VENDIDOS
# =========================
def top_vendidos_app(df):

    st.subheader("🔥 Top Vendidos")

    top = df.sort_values(
        "SALIDA",
        ascending=False
    ).head(20)

    card_kpi(
        "🔥 Productos Top",
        len(top),
        "#e74c3c"
    )

    fig = px.bar(
        top,
        x="NOMBRE_PRODUCTO",
        y="SALIDA",
        text="SALIDA",
        title="Productos más vendidos"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        top,
        use_container_width=True
    )


# =========================
# BAJA ROTACIÓN
# =========================
def baja_rotacion_app(df):

    st.subheader("🐢 Baja Rotación")

    baja = df[
        df["SALIDA"] <= 5
    ]

    card_kpi(
        "🐢 Productos Lentos",
        len(baja),
        "#f39c12"
    )

    if baja.empty:
        st.success("✅ No hay productos lentos")
        return

    fig = px.bar(
        baja.head(15),
        x="NOMBRE_PRODUCTO",
        y="SALIDA",
        text="SALIDA",
        title="Productos de baja rotación"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        baja,
        use_container_width=True
    )


# =========================
# ENTRADAS VS SALIDAS
# =========================
def entradas_salidas_app(df):

    st.subheader("📊 Entradas vs Salidas")

    total_entrada = int(df["ENTRADA"].sum())
    total_salida = int(df["SALIDA"].sum())

    c1, c2 = st.columns(2)

    with c1:
        card_kpi(
            "📥 Entradas",
            total_entrada,
            "#3498db"
        )

    with c2:
        card_kpi(
            "📤 Salidas",
            total_salida,
            "#e74c3c"
        )

    resumen = {
        "Tipo": ["Entradas", "Salidas"],
        "Total": [total_entrada, total_salida]
    }

    fig = px.pie(
        resumen,
        names="Tipo",
        values="Total",
        title="Distribución Entradas vs Salidas"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================
# DETALLE ROTACIÓN
# =========================
def detalle_rotacion_app(df):

    st.subheader("📋 Detalle Rotación")

    st.dataframe(
        df.sort_values(
            "SALIDA",
            ascending=False
        ),
        use_container_width=True
    )
