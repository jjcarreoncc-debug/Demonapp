import streamlit as st

from inventarios_app import inventarios_app
from compras_app import compras_app
from logistica_app import logistica_app
from wms_app import wms_app
from mantenimiento_app import mantenimiento_app


def simular_login():
    st.session_state.autenticado = True
    st.session_state.usuario = "JCERVANTES"
    st.session_state.nombre = "JOSE JUANCERVANTES"
    st.session_state.rol = 1
    st.session_state.perfil = "ALL"
    st.session_state.menu_mantenimiento = "🏠 Inicio"


simular_login()

st.sidebar.title("📦 MENÚ TEMPORAL")

opcion = st.sidebar.radio(
    "Selecciona módulo",
    [
        "Inventarios",
        "Compras",
        "Logística",
        "WMS",
        "Mantenimiento"
    ]
)

if opcion == "Inventarios":
    inventarios_app()

elif opcion == "Compras":
    compras_app()

elif opcion == "Logística":
    logistica_app()

elif opcion == "WMS":
    wms_app()

elif opcion == "Mantenimiento":
    mantenimiento_app()
