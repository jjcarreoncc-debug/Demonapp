import pandas as pd
import streamlit as st


# =========================
# CARGA AUTOMÁTICA LOGÍSTICA
# =========================
def cargar_datos_logistica():

    try:

        transito = pd.read_excel(
            "data/logistica/transito.xlsx"
        )

        bodegas = pd.read_excel(
            "data/logistica/bodegas.xlsx"
        )

        transportistas = pd.read_excel(
            "data/logistica/transportistas.xlsx"
        )

        rutas = pd.read_excel(
            "data/logistica/rutas.xlsx"
        )

        recepcion = pd.read_excel(
            "data/logistica/recepcion.xlsx"
        )

        despachos = pd.read_excel(
            "data/logistica/despachos.xlsx"
        )

        return (
            transito,
            bodegas,
            transportistas,
            rutas,
            recepcion,
            despachos
        )

    except Exception as e:

        st.error("❌ Error cargando archivos automáticos.")

        st.exception(e)

        return (
            None,
            None,
            None,
            None,
            None,
            None
        )
