
import pandas as pd
import streamlit as st


def cargar_datos_wms():

    try:
        inventario = pd.read_excel("data/wms/inventario_wms.xlsx")
        ubicaciones = pd.read_excel("data/wms/ubicaciones.xlsx")
        entradas = pd.read_excel("data/wms/entradas_wms.xlsx")
        salidas = pd.read_excel("data/wms/salidas_wms.xlsx")
        picking = pd.read_excel("data/wms/picking.xlsx")
        packing = pd.read_excel("data/wms/packing.xlsx")
        movimientos = pd.read_excel("data/wms/movimientos_wms.xlsx")

        return (
            inventario,
            ubicaciones,
            entradas,
            salidas,
            picking,
            packing,
            movimientos
        )

    except Exception as e:
        st.error("❌ Error cargando archivos automáticos de WMS.")
        st.exception(e)

        return (
            None,
            None,
            None,
            None,
            None,
            None,
            None
        )
