
import streamlit as st
import pandas as pd

from logistica_utils import (
    limpiar_columnas,
    buscar_columna,
    contar_estado,
    sumar_columna
)


# =========================
# DASHBOARD OPERATIVO
# =========================
def logistica_operativa_app(
    transito,
    recepcion,
    despachos,
    transportistas,
    rutas
):

    st.subheader("⚙️ Indicadores Operativos")

    # =========================
    # LIMPIAR COLUMNAS
    # =========================
    transito = limpiar_columnas(transito)
    recepcion = limpiar_columnas(recepcion)
    despachos = limpiar_columnas(despachos)
    transportistas = limpiar_columnas(transportistas)
    rutas = limpiar_columnas(rutas)

    # =========================
    # BUSCAR COLUMNAS
    # ==========================
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

    col_cantidad = buscar_columna(
        transito,
        ["CANTIDAD", "UNIDADES"]
    )

    # =========================
    # KPIs
    # =========================
    retrasados = contar_estado(
        transito,
        col_estado_transito,
        "RETRASADO"
    )

    entregados = contar_estado(
        transito,
        col_estado_transito,
        "ENTREGADO"
    )

    parciales = contar_estado(
        recepcion,
        col_estado_recepcion,
        "PARCIAL"
    )

    pendientes = contar_estado(
        despachos,
        col_estado_despacho,
        "PENDIENTE"
    )

    unidades = sumar_columna(
        transito,
        col_cantidad
    )

    total_transitos = len(transito)

    # =========================
    # PORCENTAJES
    # =========================
    if total_transitos > 0:
        porcentaje_retrasos = (
            retrasados / total_transitos
        ) * 100
    else:
        porcentaje_retrasos = 0

    # =========================
    # TARJETAS
    # =========================
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🔴 Retrasados",
        f"{retrasados:,}"
    )

    c2.metric(
        "✅ Entregados",
        f"{entregados:,}"
    )

    c3.metric(
        "📦 Unidades",
        f"{unidades:,.0f}"
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "📥 Recepciones parciales",
        f"{parciales:,}"
    )

    c5.metric(
        "📤 Pendientes",
        f"{pendientes:,}"
    )

    c6.metric(
        "⚠️ % Retrasos",
        f"{porcentaje_retrasos:.1f}%"
    )

    st.divider()

    # =========================
    # TABLAS OPERATIVAS
    # =========================
    st.subheader("🚚 Tránsitos retrasados")

    if col_estado_transito is not None:

        tabla_retrasados = transito[
            transito[col_estado_transito]
            .astype(str)
            .str.upper()
            .str.strip() == "RETRASADO"
        ]

        st.dataframe(
            tabla_retrasados,
            use_container_width=True
        )

    st.subheader("📤 Despachos pendientes")

    if col_estado_despacho is not None:

        tabla_pendientes = despachos[
            despachos[col_estado_despacho]
            .astype(str)
            .str.upper()
            .str.strip() == "PENDIENTE"
        ]

        st.dataframe(
            tabla_pendientes,
            use_container_width=True
        )
