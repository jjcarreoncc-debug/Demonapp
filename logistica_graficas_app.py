import streamlit as st
import pandas as pd

from logistica_utils import limpiar_columnas, buscar_columna


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

    # =========================
    # BUSCAR COLUMNAS
    # =========================
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

    # =========================
    # GRÁFICAS TRANSITO
    # =========================
    st.subheader("🚛 Tránsito")

    if col_estado_transito is not None:
        graf_estado_transito = (
            transito[col_estado_transito]
            .astype(str)
            .str.upper()
            .str.strip()
            .value_counts()
            .reset_index()
        )

        graf_estado_transito.columns = ["Estado", "Cantidad"]

        st.bar_chart(
            graf_estado_transito,
            x="Estado",
            y="Cantidad"
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

            ranking_retrasos.columns = ["Transportista", "Retrasos"]

            st.subheader("🔴 Top transportistas con retrasos")

            st.bar_chart(
                ranking_retrasos,
                x="Transportista",
                y="Retrasos"
            )

    if col_transportista is not None and col_cantidad is not None:
        unidades_transportista = (
            transito
            .groupby(col_transportista)[col_cantidad]
            .sum()
            .reset_index()
            .sort_values(col_cantidad, ascending=False)
            .head(10)
        )

        unidades_transportista.columns = ["Transportista", "Unidades"]

        st.subheader("📦 Unidades por transportista")

        st.bar_chart(
            unidades_transportista,
            x="Transportista",
            y="Unidades"
        )

    st.divider()

    # =========================
    # GRÁFICAS RECEPCIÓN
    # =========================
    st.subheader("📥 Recepción")

    if col_estado_recepcion is not None:
        graf_estado_recepcion = (
            recepcion[col_estado_recepcion]
            .astype(str)
            .str.upper()
            .str.strip()
            .value_counts()
            .reset_index()
        )

        graf_estado_recepcion.columns = ["Estado", "Cantidad"]

        st.bar_chart(
            graf_estado_recepcion,
            x="Estado",
            y="Cantidad"
        )
    else:
        st.warning("No se encontró columna de estado de recepción.")

    st.divider()

    # =========================
    # GRÁFICAS DESPACHOS
    # =========================
    st.subheader("📤 Despachos")

    if col_estado_despacho is not None:
        graf_estado_despacho = (
            despachos[col_estado_despacho]
            .astype(str)
            .str.upper()
            .str.strip()
            .value_counts()
            .reset_index()
        )

        graf_estado_despacho.columns = ["Estado", "Cantidad"]

        st.bar_chart(
            graf_estado_despacho,
            x="Estado",
            y="Cantidad"
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

            ranking_bodega.columns = ["Bodega", "Pendientes"]

            st.subheader("🏬 Despachos pendientes por bodega")

            st.bar_chart(
                ranking_bodega,
                x="Bodega",
                y="Pendientes"
            )

    st.divider()

    # =========================
    # COSTOS
    # =========================
    st.subheader("💰 Costos")

    if col_nombre_transportista is not None and col_costo_flete is not None:
        costos_transportista = (
            transportistas
            .groupby(col_nombre_transportista)[col_costo_flete]
            .sum()
            .reset_index()
            .sort_values(col_costo_flete, ascending=False)
            .head(10)
        )

        costos_transportista.columns = ["Transportista", "Costo"]

        st.bar_chart(
            costos_transportista,
            x="Transportista",
            y="Costo"
        )
    else:
        st.warning("No se encontraron columnas de costo por transportista.")
