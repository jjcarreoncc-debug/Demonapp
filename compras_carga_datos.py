import pandas as pd
import streamlit as st


# =========================
# CARGA AUTOMÁTICA COMPRAS
# =========================
def cargar_datos_compras():

    try:

        compras = pd.read_excel(
            "data/compras/compras.xlsx"
        )

        productos = pd.read_excel(
            "data/compras/productos.xlsx"
        )

        proveedores = pd.read_excel(
            "data/compras/proveedores.xlsx"
        )

        bodegas = pd.read_excel(
            "data/compras/bodegas.xlsx"
        )

        segmentacion = pd.read_excel(
            "data/compras/segmentacion.xlsx"
        )

        return (
            compras,
            productos,
            proveedores,
            bodegas,
            segmentacion
        )

    except Exception as e:

        st.error(
            "❌ Error cargando archivos automáticos de compras."
        )

        st.exception(e)

        return (
            None,
            None,
            None,
            None,
            None
        )
