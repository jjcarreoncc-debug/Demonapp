import streamlit as st

def simular_login():

    st.session_state.autenticado = True

    st.session_state.usuario = "JCERVANTES"

    st.session_state.nombre = "JOSE JUANCERVANTES"

    st.session_state.rol = 1

    st.session_state.perfil = "ALL"

from mantenimiento_app import mantenimiento_app

simular_login()

mantenimiento_app()
