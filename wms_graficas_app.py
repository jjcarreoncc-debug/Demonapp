import streamlit as st
import pandas as pd
import plotly.express as px


def wms_graficas_app(
    inventario,
    ubicaciones,
    entradas,
    salidas,
    picking,
    packing,
    movimientos
):

    st.subheader("📈 Gráficas WMS")

    movimientos = movimientos.copy()
    entradas = entradas.copy()
    salidas = salidas.copy()
    inventario = inventario.copy()

    for df in [
        movimientos,
        entradas,
        salidas,
        inventario
    ]:
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

    # =========================
    # MOVIMIENTOS POR TIPO
    # =========================
    if "TIPO_MOVIMIENTO" in movimientos.columns:

        tipos = (
            movimientos
            .groupby("TIPO_MOVIMIENTO")
            .size()
            .reset_index(name="Cantidad")
        )

        fig = px.bar(
            tipos,
            x="TIPO_MOVIMIENTO",
            y="Cantidad",
            text="Cantidad",
            title="Movimientos por tipo",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="movimientos_tipo"
        )

    # =========================
    # TENDENCIA MOVIMIENTOS
    # =========================
    if "FECHA_MOVIMIENTO" in movimientos.columns:

        movimientos["FECHA_MOVIMIENTO"] = pd.to_datetime(
            movimientos["FECHA_MOVIMIENTO"],
            errors="coerce"
        )

        tendencia = (
            movimientos
            .dropna(subset=["FECHA_MOVIMIENTO"])
            .groupby(
                movimientos["FECHA_MOVIMIENTO"]
                .dt.to_period("M")
                .astype(str)
            )
            .size()
            .reset_index(name="Movimientos")
        )

        tendencia.columns = [
            "Mes",
            "Movimientos"
        ]

        fig = px.line(
            tendencia,
            x="Mes",
            y="Movimientos",
            markers=True,
            title="Tendencia de movimientos",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="tendencia_movimientos"
        )

    # =========================
    # ENTRADAS VS SALIDAS
    # =========================
    entradas_total = len(entradas)
    salidas_total = len(salidas)

    comparativo = pd.DataFrame({
        "Proceso": ["Entradas", "Salidas"],
        "Cantidad": [entradas_total, salidas_total]
    })

    fig = px.pie(
        comparativo,
        names="Proceso",
        values="Cantidad",
        title="Entradas vs Salidas"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="entradas_salidas"
    )

    # =========================
    # TOP PRODUCTOS INVENTARIO
    # =========================
    if (
        "NOMBRE_PRODUCTO" in inventario.columns
        and "STOCK_ACTUAL" in inventario.columns
    ):

        inventario["STOCK_ACTUAL"] = pd.to_numeric(
            inventario["STOCK_ACTUAL"],
            errors="coerce"
        ).fillna(0)

        top_productos = (
            inventario
            .groupby("NOMBRE_PRODUCTO")["STOCK_ACTUAL"]
            .sum()
            .reset_index()
            .sort_values(
                "STOCK_ACTUAL",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            top_productos,
            x="STOCK_ACTUAL",
            y="NOMBRE_PRODUCTO",
            orientation="h",
            text="STOCK_ACTUAL",
            title="Top productos por stock",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="top_stock"
        )

    # =========================
    # PICKING
    # =========================
    if "ESTADO_PICKING" in picking.columns:

        pick = (
            picking
            .groupby("ESTADO_PICKING")
            .size()
            .reset_index(name="Cantidad")
        )

        fig = px.bar(
            pick,
            x="ESTADO_PICKING",
            y="Cantidad",
            text="Cantidad",
            title="Estado Picking",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="estado_picking"
        )

    # =========================
    # PACKING
    # =========================
    if "ESTADO_PACKING" in packing.columns:

        pack = (
            packing
            .groupby("ESTADO_PACKING")
            .size()
            .reset_index(name="Cantidad")
        )

        fig = px.bar(
            pack,
            x="ESTADO_PACKING",
            y="Cantidad",
            text="Cantidad",
            title="Estado Packing",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="estado_packing"
        )
