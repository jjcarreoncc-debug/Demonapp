# =========================
# IMPORTS APPS
# =========================
import streamlit as st
from sidebar_inventarios import sidebar_inventarios

from alta_material_app import alta_material_app
from baja_material_app import baja_material_app
from consulta_material_app import consulta_material_app
from entrada_compras_app import entrada_compras_app


# =========================
# APP INVENTARIOS
# =========================
def inventarios_app():

    menu_inv, submenu_inv, opcion_inv = sidebar_inventarios()

    st.caption(f"{menu_inv} / {submenu_inv} / {opcion_inv}")

    opcion_limpia = str(opcion_inv).strip().lower()

    if opcion_inv == "Alta de material":
        alta_material_app()

    elif opcion_inv == "Baja de material":
        baja_material_app()

    elif opcion_inv == "Consulta de material":
        consulta_material_app()

    elif opcion_limpia in [
        "registrar entrada compra",
        "registrar entrada de compra",
        "registrar entrada compras",
        "registrar entrada de compras"
    ]:
        entrada_compras_app()

    elif opcion_inv == "Alta de SKU":
        st.info("Pantalla Alta de SKU en construcción")

    elif opcion_inv == "Baja de SKU":
        st.info("Pantalla Baja de SKU en construcción")

    elif opcion_inv == "Consulta de SKU":
        st.info("Pantalla Consulta de SKU en construcción")

    else:
        st.title(opcion_inv)


# =========================
# EJECUCIÓN DIRECTA
# =========================
if __name__ == "__main__":
    inventarios_app()
