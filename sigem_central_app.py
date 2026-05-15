import streamlit as st

from auth_app import login_app, logout_app
from Minventarios_app import inventarios_app
from sidebar_analitico import analitico_app
from mantenimiento_app import mantenimiento_app
from Mlogistica_app import logistica_app
from menu_dinamico import sidebar_dinamico


# =====================================================
# LOGIN
# =====================================================

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "rol" not in st.session_state:
    st.session_state.rol = None

if not st.session_state.autenticado:
    login_app()
    st.stop()

logout_app()


    # =====================================================
    # MENU DINAMICO
    # =====================================================
    
    ruta = sidebar_dinamico()
    
    
    # =====================================================
    # ROUTER CENTRAL
    # =====================================================
st.write("DEBUG ruta:", ruta)
st.write("DEBUG rol:", st.session_state.get("rol"))
st.write("DEBUG usuario:", st.session_state.get("usuario"))

if ruta == "inicio":

    st.empty()

elif ruta == "inventarios":

    inventarios_app()

elif ruta == "logistica":

    logistica_app()

elif ruta == "analiticos":

    analitico_app()

elif ruta == "mantenimiento":

    mantenimiento_app()

else:

    st.warning(f"Ruta no configurada: {ruta}")
