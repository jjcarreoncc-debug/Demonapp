import streamlit as st
import pandas as pd


# =========================
# INDICADORES LOGÍSTICOS
# =========================
def indicadores_logistica_app(
    transito,
    recepcion,
    despachos,
    transportistas,
    rutas
):

    st.title("📊 Indicadores Logísticos")

    transito = transito.copy()
    recepcion = recepcion.copy()
    despachos = despachos.copy()
    transportistas = transportistas.copy()
    rutas = rutas.copy()
    
    for df in [transito, recepcion, despachos, transportistas, rutas]:
    df.columns = df.columns.astype(str).str.strip()
    st.write("Columnas despachos:", list(despachos.columns))
    # =========================
    # INDICADORES
    # =========================
    retrasados = len(
        transito[
            transito["ESTADO_TRANSITO"]
            .astype(str)
            .str.upper()
            .str.strip() == "RETRASADO"
        ]
    )

    en_transito = transito[
        transito["ESTADO_TRANSITO"]
        .astype(str)
        .str.upper()
        .str.strip() == "EN_TRANSITO"
    ]

    unidades_transito = pd.to_numeric(
        en_transito["CANTIDAD"],
        errors="coerce"
    ).fillna(0).sum()

    parciales = len(
        recepcion[
            recepcion["ESTADO_RECEPCION"]
            .astype(str)
            .str.upper()
            .str.strip() == "PARCIAL"
        ]
    )

    pendientes = len(
        despachos[
            despachos["ESTADO_DESPACHO"]
            .astype(str)
            .str.upper()
            .str.strip() == "PENDIENTE"
        ]
    )

    # =========================
    # FECHAS
    # =========================
    transito["FECHA_SALIDA"] = pd.to_datetime(
        transito["FECHA_SALIDA"],
        errors="coerce"
    )

    transito["FECHA_LLEGADA"] = pd.to_datetime(
        transito["FECHA_LLEGADA"],
        errors="coerce"
    )

    transito["TIEMPO_ENTREGA"] = (
        transito["FECHA_LLEGADA"] - transito["FECHA_SALIDA"]
    ).dt.days

    promedio_entrega = transito["TIEMPO_ENTREGA"].mean()

    if pd.isna(promedio_entrega):
        promedio_entrega = 0

    # Evitar valores absurdos
    if promedio_entrega > 365:
        promedio_entrega = 0

    costo_total = pd.to_numeric(
        transportistas["COSTO_FLETE"],
        errors="coerce"
    ).fillna(0).sum()

    costo_promedio = pd.to_numeric(
        rutas["COSTO_ESTIMADO"],
        errors="coerce"
    ).mean()

    if pd.isna(costo_promedio):
        costo_promedio = 0

    # =========================
    # TARJETAS
    # =========================
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🔴 Tránsitos retrasados",
        f"{retrasados:,}"
    )

    c2.metric(
        "📦 Unidades en tránsito",
        f"{unidades_transito:,.0f}"
    )

    c3.metric(
        "📥 Recepciones parciales",
        f"{parciales:,}"
    )

    c4.metric(
        "📤 Despachos pendientes",
        f"{pendientes:,}"
    )

    c5, c6, c7 = st.columns(3)

    c5.metric(
        "⏱️ Tiempo promedio entrega",
        f"{round(promedio_entrega,1)} días"
    )

    c6.metric(
        "💰 Costo total transporte",
        f"${costo_total:,.0f}"
    )

    c7.metric(
        "🛣️ Costo promedio ruta",
        f"${costo_promedio:,.2f}"
    )

    st.divider()

    # =========================
    # TABLA RESUMEN
    # =========================
    st.subheader("📋 Resumen General")

    resumen = pd.DataFrame({
        "Indicador": [
            "Tránsitos retrasados",
            "Unidades en tránsito",
            "Recepciones parciales",
            "Despachos pendientes",
            "Tiempo promedio entrega",
            "Costo total transporte",
            "Costo promedio ruta"
        ],
        "Valor": [
            retrasados,
            unidades_transito,
            parciales,
            pendientes,
            round(promedio_entrega, 1),
            costo_total,
            round(costo_promedio, 2)
        ]
    })

    st.dataframe(
        resumen,
        use_container_width=True
    )
