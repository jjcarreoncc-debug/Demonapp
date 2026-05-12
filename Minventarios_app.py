# =========================
# IMPORTS APPS
# =========================
import streamlit as st
from sidebar_inventarios import sidebar_inventarios

from alta_material_app import alta_material_app
from baja_material_app import baja_material_app
from consulta_material_app import consulta_material_app
from entrada_compras_app import entrada_compras_app
from consulta_entradas_compras_app import consulta_entradas_compras_app
from salidas_inventario_app import salidas_inventario_app
from kardex_inventario_app import kardex_inventario_app
from inventario_fisico_app import inventario_fisico_app


# =========================
# APP INVENTARIOS
# =========================
def inventarios_app():

    menu_inv, submenu_inv, opcion_inv = sidebar_inventarios()

    st.caption(f"{menu_inv} / {submenu_inv} / {opcion_inv}")

    opcion_limpia = str(opcion_inv).strip().lower()

    # =========================
    # MATERIALES
    # =========================
    if opcion_limpia == "alta de material":
        alta_material_app()

    elif opcion_limpia == "baja de material":
        baja_material_app()

    elif opcion_limpia == "consulta de material":
        consulta_material_app()

    # =========================
    # ENTRADAS
    # =========================
    elif opcion_limpia in [
        "registrar entrada compra",
        "registrar entrada de compra",
        "registrar entrada compras",
        "registrar entrada de compras"
    ]:
        entrada_compras_app()

    elif opcion_limpia == "consultar entradas compra":
        consulta_entradas_compras_app()

    # =========================
    # SALIDAS
    # =========================
    elif opcion_limpia == "registrar salida venta":
        salidas_inventario_app()

    # =========================
    # KARDEX
    # =========================
    elif opcion_limpia == "kardex por material":
        kardex_inventario_app()

    # =========================
    # INVENTARIO FÍSICO
    # =========================
    elif opcion_limpia == "crear conteo":
        inventario_fisico_app

    elif opcion_limpia == "capturar conteo":
        inventario_fisico_app

    elif opcion_limpia == "consultar conteos":
        inventario_fisico_app

    elif opcion_limpia == "aplicar ajuste":
        inventario_fisico_app

    elif opcion_limpia == "consultar ajustes":
        inventario_fisico_app

    elif opcion_limpia == "diferencias por conteo":
        inventario_fisico_app

    elif opcion_limpia == "diferencias valorizadas":
        inventario_fisico_app

    # =========================
    # SKU
    # =========================
    elif opcion_limpia == "alta de sku":
        st.info("Pantalla Alta de SKU en construcción")

    elif opcion_limpia == "baja de sku":
        st.info("Pantalla Baja de SKU en construcción")

    elif opcion_limpia == "consulta de sku":
        st.info("Pantalla Consulta de SKU en construcción")

    # =========================
    # DEFAULT
    # =========================
    else:
        st.title(opcion_inv)


# =========================
# EJECUCIÓN DIRECTA
# =========================
if __name__ == "__main__":
    inventarios_app()
