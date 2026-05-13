import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

from sigem_db import get_db_path


# =====================================================
# OBTENER EMBARQUES
# =====================================================

def obtener_embarques():

    conn = sqlite3.connect(
        get_db_path("logistica")
    )

    query = """
        SELECT
            folio_embarque,
            folio_hoja_carga,
            folio_ruta,
            pedido,
            fecha,
            cliente,
            destino,
            transportista,
            vehiculo,
            placas,
            operador,
            ruta,
            estatus
        FROM embarques
        ORDER BY fecha DESC, folio_embarque DESC
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


# =====================================================
# GRAFICA STATUS
# =====================================================

def pintar_barra_estatus(df):

    # =====================================================
    # COLORES POR ESTATUS
    # =====================================================

    mapa_colores = {

        "En almacén": "#7C3AED",
        "En patio": "#F97316",
        "Ya salió": "#EAB308",
        "En tránsito": "#2563EB",
        "Entregado": "#16A34A",
        "Cancelado": "#DC2626"

    }

    # =====================================================
    # DATAFRAME DINAMICO
    # =====================================================

    df_status = (

        df["estatus"]
        .fillna("Sin estatus")
        .astype(str)
        .value_counts()
        .reset_index()

    )

    df_status.columns = [
        "estatus",
        "cantidad"
    ]

    # =====================================================
    # SOLO ESTATUS CON DATOS
    # =====================================================

    df_status = df_status[
        df_status["cantidad"] > 0
    ]

    # =====================================================
    # COLOR DINAMICO
    # =====================================================

    colores = [

        mapa_colores.get(
            estatus,
            "#6B7280"
        )

        for estatus in df_status["estatus"]

    ]

    # =====================================================
    # GRAFICA
    # =====================================================

    chart = (

        alt.Chart(df_status)

        .mark_bar(
            cornerRadiusTopRight=8,
            cornerRadiusBottomRight=8
        )

        .encode(

            y=alt.Y(
                "estatus:N",
                sort="-x",
                title=None
            ),

            x=alt.X(
                "cantidad:Q",
                title="Cantidad de embarques",
                axis=alt.Axis(
                    format="d",
                    tickMinStep=1
                )
            ),

            color=alt.Color(
                "estatus:N",
                scale=alt.Scale(
                    domain=df_status["estatus"].tolist(),
                    range=colores
                ),
                legend=None
            ),

            tooltip=[
                alt.Tooltip(
                    "estatus:N",
                    title="Estatus"
                ),
                alt.Tooltip(
                    "cantidad:Q",
                    title="Cantidad",
                    format="d"
                )
            ]

        )

        .properties(
            height=350
        )

    )

    st.altair_chart(
        chart,
        use_container_width=True
    )


# =====================================================
# APP
# =====================================================

def dashboard_embarques_app():

    st.title(
        "📊 Dashboard embarques"
    )

    try:

        df = obtener_embarques()

    except Exception as e:

        st.error(
            "❌ Error consultando embarques"
        )

        st.exception(e)

        return

    if df.empty:

        st.warning(
            "No existen embarques registrados."
        )

        return

    # =====================================================
    # FECHAS
    # =====================================================

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        errors="coerce"
    )

    # =====================================================
    # FILTROS
    # =====================================================

    st.subheader(
        "🔎 Filtros"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        filtro_cliente = st.text_input(
            "Cliente"
        )

    with col2:

        filtro_transportista = st.text_input(
            "Transportista"
        )

    with col3:

        filtro_estatus = st.selectbox(
            "Estatus",
            ["Todos"] + sorted(
                df["estatus"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
        )

    # =====================================================
    # FILTRADO
    # =====================================================

    df_filtrado = df.copy()

    if filtro_cliente:

        df_filtrado = df_filtrado[
            df_filtrado["cliente"]
            .astype(str)
            .str.contains(
                filtro_cliente,
                case=False,
                na=False
            )
        ]

    if filtro_transportista:

        df_filtrado = df_filtrado[
            df_filtrado["transportista"]
            .astype(str)
            .str.contains(
                filtro_transportista,
                case=False,
                na=False
            )
        ]

    if filtro_estatus != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["estatus"]
            .astype(str)
            == filtro_estatus
        ]

    # =====================================================
    # KPIS
    # =====================================================

    total = len(
        df_filtrado
    )

    entregados = df_filtrado[
        df_filtrado["estatus"]
        .astype(str)
        .str.lower()
        .str.contains(
            "entregado",
            na=False
        )
    ].shape[0]

    transito = df_filtrado[
        df_filtrado["estatus"]
        .astype(str)
        .str.lower()
        .str.contains(
            "tránsito|transito",
            na=False
        )
    ].shape[0]

    pendientes = (
        total - entregados
    )

    cumplimiento = (

        round(
            (entregados / total) * 100,
            1
        )

        if total > 0 else 0

    )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📦 Embarques",
        total
    )

    c2.metric(
        "🚚 En tránsito",
        transito
    )

    c3.metric(
        "⏳ Pendientes",
        pendientes
    )

    c4.metric(
        "✅ Cumplimiento",
        f"{cumplimiento}%"
    )

    st.divider()

    # =====================================================
    # GRAFICA
    # =====================================================

    st.subheader(
        "🚦 Distribución por estatus"
    )

    pintar_barra_estatus(
        df_filtrado
    )

    st.divider()

    # =====================================================
    # TABLA
    # =====================================================

    st.subheader(
        "📋 Base del dashboard"
    )

    columnas = [

        "estatus",
        "folio_embarque",
        "folio_hoja_carga",
        "fecha",
        "cliente",
        "destino",
        "transportista",
        "vehiculo",
        "placas",
        "ruta"

    ]

    columnas = [

        col for col in columnas
        if col in df_filtrado.columns

    ]

    st.dataframe(
        df_filtrado[columnas],
        use_container_width=True,
        height=450,
        hide_index=True
    )
