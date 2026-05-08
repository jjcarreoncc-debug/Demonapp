import streamlit as st
import pandas as pd


def wms_dashboard_app(
    inventario,
    ubicaciones,
    entradas,
    salidas,
    picking,
    packing,
    movimientos
):

    st.subheader("📊 Resumen Ejecutivo WMS")

    inventario = inventario.copy()
    ubicaciones = ubicaciones.copy()
    entradas = entradas.copy()
    salidas = salidas.copy()
    picking = picking.copy()
    packing = packing.copy()
    movimientos = movimientos.copy()

    for df in [
        inventario,
        ubicaciones,
        entradas,
        salidas,
        picking,
        packing,
        movimientos
    ]:
        df.columns = df.columns.astype(str).str.strip()

    stock_total = (
        pd.to_numeric(inventario["STOCK_ACTUAL"], errors="coerce")
        .fillna(0)
        .sum()
        if "STOCK_ACTUAL" in inventario.columns
        else 0
    )

    stock_critico = (
        len(inventario[
            inventario["ESTADO_STOCK"].astype(str).str.upper().str.strip() == "CRITICO"
        ])
        if "ESTADO_STOCK" in inventario.columns
        else 0
    )

    ubicaciones_activas = (
        len(ubicaciones[
            ubicaciones["ESTADO_UBICACION"].astype(str).str.upper().str.strip() == "ACTIVA"
        ])
        if "ESTADO_UBICACION" in ubicaciones.columns
        else len(ubicaciones)
    )

    entradas_total = len(entradas)
    salidas_total = len(salidas)
    movimientos_total = len(movimientos)

    picking_completado = (
        len(picking[
            picking["ESTADO_PICKING"].astype(str).str.upper().str.strip() == "COMPLETADO"
        ])
        if "ESTADO_PICKING" in picking.columns
        else 0
    )

    packing_completado = (
        len(packing[
            packing["ESTADO_PACKING"].astype(str).str.upper().str.strip() == "COMPLETADO"
        ])
        if "ESTADO_PACKING" in packing.columns
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("📦 Stock total", f"{stock_total:,.0f}")
    c2.metric("⚠️ Stock crítico", f"{stock_critico:,}")
    c3.metric("🏬 Ubicaciones activas", f"{ubicaciones_activas:,}")
    c4.metric("🔄 Movimientos", f"{movimientos_total:,}")

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("📥 Entradas", f"{entradas_total:,}")
    c6.metric("📤 Salidas", f"{salidas_total:,}")
    c7.metric("✅ Picking completado", f"{picking_completado:,}")
    c8.metric("📦 Packing completado", f"{packing_completado:,}")

    st.divider()

    st.subheader("📋 Últimos movimientos")

    if "FECHA_MOVIMIENTO" in movimientos.columns:
        movimientos["FECHA_MOVIMIENTO"] = pd.to_datetime(
            movimientos["FECHA_MOVIMIENTO"],
            errors="coerce"
        )

        ultimos = (
            movimientos
            .sort_values("FECHA_MOVIMIENTO", ascending=False)
            .head(20)
        )
    else:
        ultimos = movimientos.head(20)

    st.dataframe(
        ultimos,
        use_container_width=True
    )
