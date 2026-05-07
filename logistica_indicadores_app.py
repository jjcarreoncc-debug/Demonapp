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

    # Copias para no dañar los datos originales
    transito = transito.copy()
    recepcion = recepcion.copy()
    despachos = despachos.copy()
    transportistas = transportistas.copy()
    rutas = rutas.copy()

    # =========================
    # Retrasos
    # =========================
    if "ESTADO_TRANSITO" in transito.columns:
        retrasados = transito[
            transito["ESTADO_TRANSITO"].astype(str).str.upper().str.strip() == "RETRASADO"
        ]
        total_retrasados = len(retrasados)
    else:
        total_retrasados = 0

    st.metric("🔴 Tránsitos retrasados", total_retrasados)

    # =========================
    # Unidades en tránsito
    # =========================
    if "ESTADO_TRANSITO" in transito.columns and "CANTIDAD" in transito.columns:
        en_transito = transito[
            transito["ESTADO_TRANSITO"].astype(str).str.upper().str.strip() == "EN_TRANSITO"
        ]
        unidades_transito = pd.to_numeric(
            en_transito["CANTIDAD"],
            errors="coerce"
        ).fillna(0).sum()
    else:
        unidades_transito = 0

    st.metric("📦 Unidades en tránsito", f"{unidades_transito:,.0f}")

    # =========================
    # Recepciones parciales
    # =========================
    if "ESTADO_RECEPCION" in recepcion.columns:
        parciales = recepcion[
            recepcion["ESTADO_RECEPCION"].astype(str).str.upper().str.strip() == "PARCIAL"
        ]
        total_parciales = len(parciales)
    else:
        total_parciales = 0

    st.metric("📥 Recepciones parciales", total_parciales)

    # =========================
    # Despachos pendientes
    # =========================
    if "ESTADO_DESPACHO" in despachos.columns:
        pendientes = despachos[
            despachos["ESTADO_DESPACHO"].astype(str).str.upper().str.strip() == "PENDIENTE"
        ]
        total_pendientes = len(pendientes)
    else:
        total_pendientes = 0

    st.metric("📤 Despachos pendientes", total_pendientes)

    # =========================
    # Tiempo promedio de entrega
    # =========================
    if "FECHA_SALIDA" in transito.columns and "FECHA_LLEGADA" in transito.columns:
        transito["FECHA_SALIDA"] = pd.to_datetime(
            transito["FECHA_SALIDA"],
            errors="coerce"
        )

        transito["FECHA_LLEGADA"] = pd.to_datetime(
            transito["FECHA_LLEGADA"],
            errors="coerce"
        )

        transito["TIEMPO_ENTREGA_DIAS"] = (
            transito["FECHA_LLEGADA"] - transito["FECHA_SALIDA"]
        ).dt.days

        promedio_entrega = transito["TIEMPO_ENTREGA_DIAS"].mean()

        if pd.isna(promedio_entrega):
            promedio_entrega_mostrar = 0
        else:
            promedio_entrega_mostrar = round(promedio_entrega, 1)
    else:
        promedio_entrega_mostrar = 0

    st.metric("⏱️ Tiempo promedio entrega (días)", promedio_entrega_mostrar)

    # =========================
    # Costo de transporte total
    # =========================
    if "COSTO_FLETE" in transportistas.columns:
        costo_total = pd.to_numeric(
            transportistas["COSTO_FLETE"],
            errors="coerce"
        ).fillna(0).sum()
    else:
        costo_total = 0

    st.metric("💰 Costo total transporte", f"${costo_total:,.0f}")

    # =========================
    # Costo promedio por ruta
    # =========================
    if "COSTO_ESTIMADO" in rutas.columns:
        costo_promedio = pd.to_numeric(
            rutas["COSTO_ESTIMADO"],
            errors="coerce"
        ).mean()

        if pd.isna(costo_promedio):
            costo_promedio_mostrar = 0
        else:
            costo_promedio_mostrar = round(costo_promedio, 2)
    else:
        costo_promedio_mostrar = 0

    st.metric("🛣️ Costo promedio por ruta", f"${costo_promedio_mostrar:,.2f}")

    st.divider()

    # =========================
    # Detalle resumido
    # =========================
    st.subheader("📋 Detalle rápido de indicadores")

    resumen = pd.DataFrame({
        "Retrasados": [total_retrasados],
        "Unidades en tránsito": [unidades_transito],
        "Recepciones parciales": [total_parciales],
        "Despachos pendientes": [total_pendientes],
        "Tiempo promedio entrega": [promedio_entrega_mostrar],
        "Costo total transporte": [costo_total],
        "Costo promedio ruta": [costo_promedio_mostrar]
    })

    st.dataframe(
        resumen,
        use_container_width=True
    )
