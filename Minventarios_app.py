# =========================
# IMPORTS APPS
# =========================
import streamlit as st
from datetime import datetime
from sidebar_inventarios import sidebar_inventarios

from alta_material_app import alta_material_app
from baja_material_app import baja_material_app
from consulta_material_app import consulta_material_app
from entrada_compras_app import entrada_compras_app
from consulta_entradas_compras_app import consulta_entradas_compras_app
from salidas_inventario_app import salidas_inventario_app
from kardex_inventario_app import kardex_inventario_app
from inventario_fisico_app import inventario_fisico_app
from ajuste_inventario_fisico_app import ajuste_inventario_fisico_app
from consulta_ajustes_app import consulta_ajustes_app
from diferencias_valorizadas_app import diferencias_valorizadas_app

from embarques_inventario_app import (
    embarques_inventario_app
)

from consulta_embarques_inventario_app import (
    consulta_embarques_inventario_app
)

from confirmacion_cancelacion_embarque_app import (
    confirmacion_cancelacion_embarque_app
)


# =========================
# INICIO INVENTARIOS
# =========================
def inicio_inventarios_app():

    st.title("📦 Inventarios")

    st.caption(
        "Gestión integral de materiales, entradas, salidas, kardex e inventario físico."
    )

    try:
        st.image(
            "logoinventarios.png",
            use_container_width=True
        )
    except Exception:
        st.info(
            "Imagen de inicio no encontrada. Verifica que exista el archivo logoinventarios.png"
        )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Módulo",
            "Inventarios"
        )

    with col2:
        st.metric(
            "Usuario",
            st.session_state.get("usuario", "SIN_USUARIO")
        )

    with col3:
        st.metric(
            "Fecha",
            datetime.now().strftime("%Y-%m-%d")
        )

    st.info(
        "Selecciona una opción del menú lateral para comenzar."
    )


# =========================
# APP INVENTARIOS
# =========================
def inventarios_app():

    menu_inv, submenu_inv, opcion_inv = sidebar_inventarios()

    st.caption(f"{menu_inv} / {submenu_inv} / {opcion_inv}")

    opcion_limpia = str(opcion_inv).strip().lower()

    # =========================
    # INICIO
    # =========================
    if opcion_limpia in [
        "inicio",
        "inicio inventarios",
        "🏠 inicio",
        "🏠 inicio inventarios"
    ]:
        inicio_inventarios_app()

    # =========================
    # MATERIALES
    # =========================
    elif opcion_limpia == "alta de material":
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

    elif opcion_limpia == "embarque":
        confirmacion_cancelacion_embarque_app()

    # =========================
    # SALIDAS
    # =========================
    elif opcion_limpia == "registrar salida venta":
        salidas_inventario_app()

    elif opcion_limpia == "embarques":
        embarques_inventario_app()

    elif opcion_limpia == "consultar embarques":
        consulta_embarques_inventario_app()

    # =========================
    # KARDEX
    # =========================
    elif opcion_limpia == "kardex por material":
        kardex_inventario_app()

    # =========================
    # INVENTARIO FÍSICO
    # =========================
    elif opcion_limpia == "crear conteo":
        inventario_fisico_app()

    elif opcion_limpia == "capturar conteo":
        inventario_fisico_app()

    elif opcion_limpia == "consultar conteos":
        inventario_fisico_app()

    elif opcion_limpia == "aplicar ajuste":
        ajuste_inventario_fisico_app()

    elif opcion_limpia == "consultar ajustes":
        consulta_ajustes_app()

    elif opcion_limpia == "diferencias por conteo":
        diferencias_valorizadas_app()

    elif opcion_limpia == "diferencias valorizadas":
        diferencias_valorizadas_app()

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
        inicio_inventarios_app()


# =========================
# EJECUCIÓN DIRECTA
# =========================
if __name__ == "__main__":
    inventarios_app()
