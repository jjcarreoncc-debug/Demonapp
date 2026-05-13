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
# GRAFICA ESTATUS POR EMBARQUE
# =====================================================

def pintar_barra_estatus(df):

    orden_estatus = [

        "Pendiente",
        "En almacén",
        "En patio",
        "Ya salió",
        "En tránsito",
        "Entregado",
        "Cancelado"

    ]

    mapa_colores = {

        "Pendiente": "#6B7280",
        "En almacén": "#7C3AED",
        "En patio": "#F97316",
        "Ya salió": "#EAB308",
        "En tránsito": "#2563EB",
        "Entregado": "#16A34A",
        "Cancelado": "#DC2626"

    }

    # =====================================================
    # DATAFRAME
    # =====================================================

    df_grafica = df.copy()

    df_grafica["estatus"] = (
        df_grafica["estatus"]
        .fillna("Pendiente")
        .astype(str)
    )

    df_grafica["embarque"] = (
        df_grafica["folio_embarque"]
        .fillna("")
        .astype(str)
    )

    df_grafica = df_grafica[
        df_grafica["embarque"] != ""
    ]

    if df_grafica.empty:

        st.warning(
            "No existen embarques para mostrar."
        )

        return

    # =====================================================
    # ORDEN DINAMICO
    # =====================================================

    estatus_presentes = [

        estatus
        for estatus in orden_estatus
        if estatus in (
            df_grafica["estatus"]
            .unique()
            .tolist()
        )

    ]

    estatus_no_catalogados = [

        estatus
        for estatus in (
            df_grafica["estatus"]
            .unique()
            .tolist()
        )
        if estatus not in orden_estatus

    ]

    orden_final = (
        estatus_presentes
        + estatus_no_catalogados
    )

    colores = [

        mapa_colores.get(
            estatus,
            "#9CA3AF"
        )

        for estatus in orden_final

    ]

    # =====================================================
    # ANCHO DINAMICO
    # =====================================================

    ancho_grafica = max(
        1400,
        len(df_grafica) * 85
    )

    # =====================================================
    # GRAFICA TIPO MATRIZ
    # =====================================================

    chart = (

        alt.Chart(df_grafica)

        .mark_rect(
            cornerRadius=5
        )

        .encode(

            x=alt.X(
                "embarque:N",
                title="Número de embarque",
                sort=None,
                axis=alt.Axis(
                    labelAngle=-45,
                    labelLimit=120
                )
            ),

            y=alt.Y(
                "estatus:N",
                sort=orden_final,
                title="Estatus"
            ),

            color=alt.Color(
                "estatus:N",
                scale=alt.Scale(
                    domain=orden_final,
                    range=colores
                ),
                legend=None
            ),

            tooltip=[

                alt.Tooltip(
                    "folio_embarque:N",
                    title="Embarque"
                ),

                alt.Tooltip(
                    "cliente:N",
                    title="Cliente"
                ),

                alt.Tooltip(
                    "destino:N",
                    title="Destino"
                ),

                alt.Tooltip(
                    "transportista:N",
                    title="Transportista"
                ),

                alt.Tooltip(
                    "vehiculo:N",
                    title="Vehículo"
                ),

                alt.Tooltip(
                    "placas:N",
                    title="Placas"
                ),

                alt.Tooltip(
                    "ruta:N",
                    title="Ruta"
                ),

                alt.Tooltip(
                    "estatus:N",
                    title="Estatus"
                )

            ]

        )

        .properties(
            width=ancho_grafica,
            height=420
        )

        .configure_view(
            stroke="#D1D5DB"
        )

    )

    st.altair_chart(
        chart,
        use_container_width=False
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

    pendientes = df_filtrado[
        df_filtrado["estatus"]
        .astype(str)
        .str.lower()
        .str.contains(
            "pendiente",
            na=False
        )
    ].shape[0]

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
