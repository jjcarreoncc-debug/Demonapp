import streamlit as st

from menu_dinamico import sidebar_dinamico
from inventarios_app import inventarios_app
from compras_app import compras_app
from logistica_app import logistica_app
from wms_app import wms_app
from mantenimiento_app import mantenimiento_app


st.set_page_config(
    page_title="SIGEM",
    layout="wide"
)

# =========================
# LOGIN TEMPORAL DESACTIVADO
# =========================

st.session_state.autenticado = True
st.session_state.usuario = "admin"
st.session_state.nombre = "Administrador"
st.session_state.rol = "Administrador"


# =========================
# NUEVO SIGEM PRINCIPAL
# =========================

#ruta = sidebar_dinamico()

ruta = "inventarios"

if ruta == "inicio":
    st.empty()

elif ruta == "inventarios":
    st.title("📦 Inventarios")
    inventarios_app()

elif ruta == "compras":
    st.title("🛒 Compras")
    compras_app()

elif ruta == "logistica":
    st.title("🚚 Logística")
    logistica_app()

elif ruta == "wms":
    st.title("🏬 WMS")
    wms_app()

elif ruta == "mantenimiento":
    st.title("🛠️ Mantenimiento")
    mantenimiento_app()

else:
    st.warning(f"Ruta no configurada: {ruta}")
