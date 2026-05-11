import streamlit as st

def simular_login():

    st.session_state.autenticado = True

    st.session_state.usuario = "JCERVANTES"

    st.session_state.nombre = "JOSE JUANCERVANTES"

    st.session_state.rol = 1

    st.session_state.perfil = "ALL"

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


simular_login()

ruta = sidebar_dinamico()

if ruta == "inventarios":
    inventarios_app()

elif ruta == "compras":
    compras_app()

elif ruta == "logistica":
    logistica_app()

elif ruta == "wms":
    wms_app()

elif ruta == "mantenimiento":
    mantenimiento_app()

else:
    st.info("Selecciona una opción del menú.")
