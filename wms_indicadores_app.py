import streamlit as st
import pandas as pd


def wms_indicadores_app(
    inventario,
    ubicaciones,
    entradas,
    salidas,
    picking,
    packing,
    movimientos
):

    st.subheader("📌 Indicadores WMS")

    inventario = inventario.copy()
    ubicaciones = ubicaciones.copy()
    entradas = entradas.copy()
    salidas = salidas.copy()
    picking = picking.copy()
    packing = packing.copy()
    movimientos = movimientos.copy()

    for df in [inventario, ubicaciones, entradas, salidas, picking, packing, movimientos]:
        df.columns = df.columns.astype(str).str.strip()

    stock_total = pd.to_numeric(
        inventario.get("STOCK_ACTUAL", 0),
        errors="coerce"
    ).fillna(0).sum()

    stock_critico = len(
        inventario[
            inventario.get("ESTADO_STOCK", "")
            .astype(str)
            .str.upper()
            .str.strip() == "CRITICO"
        ]
    ) if "ESTADO_STOCK" in inventario.columns else 0

    ubicaciones_bloqueadas = len(
        ubicaciones[
            ubicaciones.get("ESTADO_UBICACION", "")
            .astype(str)
            .str.upper()
            .str.strip() == "BLOQUEADA"
        ]
    ) if "ESTADO_UBICACION" in ubicaciones.columns else 0

    entradas_parciales = len(
        entradas[
            entradas.get("ESTADO_ENTRADA", "")
            .astype(str)
            .str.upper()
            .str.strip() == "PARCIAL"
        ]
    ) if "ESTADO_ENTRADA" in entradas.columns else 0

    salidas_parciales = len(
        salidas[
            salidas.get("ESTADO_SALIDA", "")
            .astype(str)
            .str.upper()
            .str.strip() == "PARCIAL"
        ]
    ) if "ESTADO_SALIDA" in salidas.columns else 0

    picking_pendiente = len(
        picking[
            picking.get("ESTADO_PICKING", "")
            .astype(str)
            .str.upper()
            .str.strip() == "PENDIENTE"
        ]
    ) if "ESTADO_PICKING" in picking.columns else 0

    packing_pendiente = len(
        packing[
            packing.get("ESTADO_PACKING", "")
            .astype(str)
            .str.upper()
            .str.strip() == "PENDIENTE"
        ]
    ) if "ESTADO_PACKING" in packing.columns else 0

    movimientos_pendientes = len(
        movimientos[
            movimientos.get("ESTADO_MOVIMIENTO", "")
            .astype(str)
            .str.upper()
            .str.strip() == "PENDIENTE"
        ]
    ) if "ESTADO_MOVIMIENTO" in movimientos.columns else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📦 Stock total", f"{stock_total:,.0f}")
    c2.metric("⚠️ Stock crítico", f"{stock_critico:,}")
    c3.metric("🚫 Ubicaciones bloqueadas", f"{ubicaciones_bloqueadas:,}")
    c4.metric("🔄 Movimientos pendientes", f"{movimientos_pendientes:,}")

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("📥 Entradas parciales", f"{entradas_parciales:,}")
    c6.metric("📤 Salidas parciales", f"{salidas_parciales:,}")
    c7.metric("🧺 Picking pendiente", f"{picking_pendiente:,}")
    c8.metric("📦 Packing pendiente", f"{packing_pendiente:,}")

    st.divider()

    resumen = pd.DataFrame({
        "Indicador": [
            "Stock total",
            "Stock crítico",
            "Ubicaciones bloqueadas",
            "Movimientos pendientes",
            "Entradas parciales",
            "Salidas parciales",
            "Picking pendiente",
            "Packing pendiente"
        ],
        "Valor": [
            stock_total,
            stock_critico,
            ubicaciones_bloqueadas,
            movimientos_pendientes,
            entradas_parciales,
            salidas_parciales,
            picking_pendiente,
            packing_pendiente
        ]
    })

    st.subheader("📋 Resumen de indicadores")
    st.dataframe(resumen, use_container_width=True)
