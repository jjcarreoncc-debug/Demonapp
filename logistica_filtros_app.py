import streamlit as st


# =========================
# FILTROS LOGÍSTICA
# =========================
def filtros_logistica(
    transito,
    recepcion,
    despachos
):

    filtros = {}

    st.sidebar.header("🔎 Filtros Globales")

    # =========================
    # ESTADO TRANSITO
    # =========================
    if "ESTADO_TRANSITO" in transito.columns:

        estados_transito = sorted(
            transito["ESTADO_TRANSITO"]
            .astype(str)
            .dropna()
            .unique()
        )

        filtro_estado_transito = st.sidebar.multiselect(
            "🚛 Estado tránsito",
            estados_transito
        )

        filtros["estado_transito"] = filtro_estado_transito

    # =========================
    # ESTADO RECEPCION
    # =========================
    if "ESTADO_RECEPCION" in recepcion.columns:

        estados_recepcion = sorted(
            recepcion["ESTADO_RECEPCION"]
            .astype(str)
            .dropna()
            .unique()
        )

        filtro_estado_recepcion = st.sidebar.multiselect(
            "📥 Estado recepción",
            estados_recepcion
        )

        filtros["estado_recepcion"] = filtro_estado_recepcion

    # =========================
    # ESTADO DESPACHO
    # =========================
    if "ESTADO_DESPACHO" in despachos.columns:

        estados_despacho = sorted(
            despachos["ESTADO_DESPACHO"]
            .astype(str)
            .dropna()
            .unique()
        )

        filtro_estado_despacho = st.sidebar.multiselect(
            "📤 Estado despacho",
            estados_despacho
        )

        filtros["estado_despacho"] = filtro_estado_despacho

    return filtros
