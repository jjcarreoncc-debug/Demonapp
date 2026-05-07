import streamlit as st
import pandas as pd
import plotly.express as px

from logistica_utils import limpiar_columnas, buscar_columna


def grafica_barras(
    df,
    x,
    y,
    titulo,
    subtitulo="",
    color="#0B74DE",
    formato_texto=None
):

    st.markdown(
        f"""
        <div style="
            background:#ffffff;
            padding:22px;
            border-radius:18px;
            box-shadow:0 4px 14px rgba(0,0,0,0.08);
            margin-bottom:24px;
        ">
            <h3 style="margin-bottom:4px;">{titulo}</h3>
            <p style="margin-top:0;color:#64748b;">{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df is None or len(df) == 0:
        st.info("No hay datos para mostrar.")
        return

    fig = px.bar(
        df,
        x=x,
        y=y,
        text=y,
        template="plotly_white"
    )

    fig.update_traces(
        marker_color=color,
        textposition="outside",
        texttemplate=formato_texto if formato_texto else "%{text}",
        hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>"
    )

    fig.update_layout(
        height=430,
        margin=dict(l=30, r=30, t=20, b=40),
        xaxis_title=x,
        yaxis_title=y,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial",
            size=13,
            color="#1f2937"
        ),
        xaxis=dict(
            tickangle=0,
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E5E7EB"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================
# GRÁFICAS LOGÍSTICAS
# =========================
def logistica_graficas_app(
    transito,
    recepcion,
    despachos,
    transportistas,
    rutas
):

    st.title("📈 Gráficas Operativas Logísticas")

    transito = limpiar_columnas(transito)
    recepcion = limpiar_columnas(recepcion)
    despachos = limpiar_columnas(despachos)
    transportistas = limpiar_columnas(transportistas)
    rutas = limpiar_columnas(rutas)

    col_estado_transito = buscar_columna(
        transito,
        ["ESTADO_TRANSITO", "ESTADO TRANSITO", "ESTADO"]
    )

    col_estado_recepcion = buscar_columna(
        recepcion,
        ["ESTADO_RECEPCION", "ESTADO RECEPCION", "ESTADO"]
    )

    col_estado_despacho = buscar_columna(
        despachos,
        ["ESTADO_DESPACHO", "ESTADO DESPACHO", "ESTADO"]
    )

    col_transportista = buscar_columna(
        transito,
        ["ID_TRANSPORTISTA", "TRANSPORTISTA"]
    )

    col_cantidad = buscar_columna(
        transito,
        ["CANTIDAD", "UNIDADES"]
    )

    col_bodega = buscar_columna(
        despachos,
        ["ID_BODEGA", "BODEGA"]
    )

    col_costo_flete = buscar_columna(
        transportistas,
        ["COSTO_FLETE", "COSTO FLETE"]
    )

    col_nombre_transportista = buscar_columna(
        transportistas,
        ["NOMBRE_TRANSPORTISTA", "NOMBRE TRANSPORTISTA", "TRANSPORTISTA"]
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "🚛 Tránsito",
        "📥 Recepción",
        "📤 Despachos",
        "💰 Costos"
    ])

    # =========================
    # TRÁNSITO
    # =========================
    with tab1:

        if col_estado_transito is not None:

            graf_estado_transito = (
                transito[col_estado_transito]
                .astype(str)
                .str.upper()
                .str.strip()
                .value_counts()
                .reset_index()
            )

            graf_estado_transito.columns = [
                "Estado",
                "Cantidad"
            ]

            grafica_barras(
                graf_estado_transito,
                "Estado",
                "Cantidad",
                "🚛 Estados de tránsito",
                "Distribución general de los estados de tránsito.",
                "#0B74DE"
            )

        else:
            st.warning("No se encontró columna de estado de tránsito.")

        if col_transportista is not None and col_estado_transito is not None:

            retrasos_transportista = transito[
                transito[col_estado_transito]
                .astype(str)
                .str.upper()
                .str.strip() == "RETRASADO"
            ]

            if len(retrasos_transportista) > 0:

                ranking_retrasos = (
                    retrasos_transportista[col_transportista]
                    .astype(str)
                    .value_counts()
                    .head(10)
                    .reset_index()
                )

                ranking_retrasos.columns = [
                    "Transportista",
                    "Retrasos"
                ]

                grafica_barras(
                    ranking_retrasos,
                    "Transportista",
                    "Retrasos",
                    "🔴 Top transportistas con retrasos",
                    "Transportistas con mayor número de tránsitos retrasados.",
                    "#EF4444"
                )

        if col_transportista is not None and col_cantidad is not None:

            transito[col_cantidad] = pd.to_numeric(
                transito[col_cantidad],
                errors="coerce"
            ).fillna(0)

            unidades_transportista = (
                transito
                .groupby(col_transportista)[col_cantidad]
                .sum()
                .reset_index()
                .sort_values(col_cantidad, ascending=False)
                .head(10)
            )

            unidades_transportista.columns = [
                "Transportista",
                "Unidades"
            ]

            grafica_barras(
                unidades_transportista,
                "Transportista",
                "Unidades",
                "📦 Unidades por transportista",
                "Volumen de unidades transportadas por transportista.",
                "#7C3AED"
            )

    # =========================
    # RECEPCIÓN
    # =========================
    with tab2:

        if col_estado_recepcion is not None:

            graf_estado_recepcion = (
                recepcion[col_estado_recepcion]
                .astype(str)
                .str.upper()
                .str.strip()
                .value_counts()
                .reset_index()
            )

            graf_estado_recepcion.columns = [
                "Estado",
                "Cantidad"
            ]

            grafica_barras(
                graf_estado_recepcion,
                "Estado",
                "Cantidad",
                "📥 Estados de recepción",
                "Distribución de recepciones por estado.",
                "#10B981"
            )

        else:
            st.warning("No se encontró columna de estado de recepción.")

    # =========================
    # DESPACHOS
    # =========================
    with tab3:

        if col_estado_despacho is not None:

            graf_estado_despacho = (
                despachos[col_estado_despacho]
                .astype(str)
                .str.upper()
                .str.strip()
                .value_counts()
                .reset_index()
            )

            graf_estado_despacho.columns = [
                "Estado",
                "Cantidad"
            ]

            grafica_barras(
                graf_estado_despacho,
                "Estado",
                "Cantidad",
                "📤 Estados de despacho",
                "Distribución de despachos por estado.",
                "#F59E0B"
            )

        else:
            st.warning("No se encontró columna de estado de despacho.")

        if col_bodega is not None and col_estado_despacho is not None:

            pendientes_bodega = despachos[
                despachos[col_estado_despacho]
                .astype(str)
                .str.upper()
                .str.strip() == "PENDIENTE"
            ]

            if len(pendientes_bodega) > 0:

                ranking_bodega = (
                    pendientes_bodega[col_bodega]
                    .astype(str)
                    .value_counts()
                    .head(10)
                    .reset_index()
                )

                ranking_bodega.columns = [
                    "Bodega",
                    "Pendientes"
                ]

                grafica_barras(
                    ranking_bodega,
                    "Bodega",
                    "Pendientes",
                    "🏬 Despachos pendientes por bodega",
                    "Bodegas con mayor cantidad de despachos pendientes.",
                    "#F97316"
                )

    # =========================
    # COSTOS
    # =========================
    with tab4:

        if col_nombre_transportista is not None and col_costo_flete is not None:

            transportistas[col_costo_flete] = pd.to_numeric(
                transportistas[col_costo_flete],
                errors="coerce"
            ).fillna(0)

            costos_transportista = (
                transportistas
                .groupby(col_nombre_transportista)[col_costo_flete]
                .sum()
                .reset_index()
                .sort_values(col_costo_flete, ascending=False)
                .head(10)
            )

            costos_transportista.columns = [
                "Transportista",
                "Costo"
            ]

            grafica_barras(
                costos_transportista,
                "Transportista",
                "Costo",
                "💰 Costos por transportista",
                "Costo total de flete por cada transportista.",
                "#0B74DE",
                "$%{text:,.0f}"
            )

        else:
            st.warning("No se encontraron columnas de costo por transportista.")
