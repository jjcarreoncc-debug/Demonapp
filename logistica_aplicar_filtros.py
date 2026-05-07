# =========================
# APLICAR FILTROS
# =========================
def aplicar_filtros_logistica(
    transito,
    recepcion,
    despachos,
    filtros
):

    # =========================
    # TRANSITO
    # =========================
    if (
        "estado_transito" in filtros
        and filtros["estado_transito"]
    ):

        transito = transito[
            transito["ESTADO_TRANSITO"]
            .astype(str)
            .isin(filtros["estado_transito"])
        ]

    # =========================
    # RECEPCION
    # =========================
    if (
        "estado_recepcion" in filtros
        and filtros["estado_recepcion"]
    ):

        recepcion = recepcion[
            recepcion["ESTADO_RECEPCION"]
            .astype(str)
            .isin(filtros["estado_recepcion"])
        ]

    # =========================
    # DESPACHOS
    # =========================
    if (
        "estado_despacho" in filtros
        and filtros["estado_despacho"]
    ):

        despachos = despachos[
            despachos["ESTADO_DESPACHO"]
            .astype(str)
            .isin(filtros["estado_despacho"])
        ]

    return (
        transito,
        recepcion,
        despachos
    )
