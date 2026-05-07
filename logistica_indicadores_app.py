
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

    # =========================
    # Retrasos
    # =========================
    retrasados = transito[
        transito["ESTADO_TRANSITO"].astype(str).str.upper() == "RETRASADO"
    ]
    st.metric("🔴 Tránsitos retrasados", len(retrasados))

    # =========================
    # Unidades en tránsito
    # =========================
    en_transito = transito[
        transito["ESTADO_TRANSITO"].astype(str).str.upper() == "EN_TRANSITO"
    ]
    unidades_transito = en_transito["CANTIDAD"].sum()
    st.metric("📦 Unidades en tránsito", f"{unidades_transito:,}")

    # =========================
    # Recepciones parciales
    # =========================
    parciales = recepcion[
        recepcion["ESTADO_RECEPCION"].astype(str).str.upper() == "PARCIAL"
    ]
    st.metric("📥 Recepciones parciales", len(parciales))

    # =========================
    # Despachos pendientes
    # =========================
    pendientes = despachos[
        despachos["ESTADO_DESPACHO"].astype(str).str.upper() == "PENDIENTE"
    ]
    st.metric("📤 Despachos pendientes", len(pendientes))

    # =========================
    # Tiempo promedio de entrega (días)
    # =========================
    transito["FECHA_SALIDA"] = pd.to_datetime(transito["FECHA_SALIDA"])
    transito["FECHA_LLEGADA"] = pd.to_datetime(transito["FECHA_LLEGADA"])
    transito["TIEMPO_ENTREGA_DIAS"] = (
        transito["FECHA_LLEGADA"] - transito["FECHA_SALIDA"]
    ).dt.days
    promedio_entrega = transito["TIEMPO_ENTREGA_DIAS"].mean()
    st.metric("⏱️ Tiempo promedio entrega (días)", round(promedio_entrega, 1))

    # =========================
    # Costo de transporte total
    # =========================
    costo_total = transportistas["COSTO_FLETE"].sum()
    st.metric("💰 Costo total transporte", f"${costo_total:,}")

    # =========================
    # Costo promedio por ruta
    # =========================
    costo_promedio = rutas["COSTO_ESTIMADO"].mean()
    st.metric("🛣️ Costo promedio por ruta", f"${round(costo_promedio, 2):,}")

    st.divider()

    # =========================
    # Detalle resumido
    # =========================
    st.subheader("📋 Detalle rápido de indicadores")
    st.dataframe(
        pd.DataFrame({
            "Retrasados": [len(retrasados)],
            "Unidades en tránsito": [unidades_transito],
            "Recepciones parciales": [len(parciales)],
            "Despachos pendientes": [len(pendientes)],
            "Tiempo promedio entrega": [round(promedio_entrega, 1)],
            "Costo total transporte": [costo_total],
            "Costo promedio ruta": [round(costo_promedio, 2)]
        }),
        use_container_width=True
    )
