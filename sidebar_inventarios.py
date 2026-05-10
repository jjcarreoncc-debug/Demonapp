import streamlit as st


def sidebar_inventarios():

    with st.sidebar:

        st.markdown("---")
        st.subheader("📦 Inventarios")

        opcion = st.radio(
            "Opciones Inventarios",
            [
                "Productos",
                "Entradas",
                "Salidas",
                "Transferencias",
                "Kardex",
                "Conteos cíclicos",
                "Lotes / Series"
            ],
            key="sidebar_inventarios"
        )

    return opcion
