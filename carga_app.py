import streamlit as st
import pandas as pd

def carga_app():

    st.title("📂 Carga de archtivos")

    archivo_prod = st.file_uploader("Productos")
    archivo_mov = st.file_uploader("Movimientos")
    archivo_inv = st.file_uploader("Inventario")

    if archivo_prod:
        st.session_state.productos = pd.read_excel(archivo_prod)

    if archivo_mov:
        st.session_state.movimientos = pd.read_excel(archivo_mov)

    if archivo_inv:
        st.session_state.inventario = pd.read_excel(archivo_inv)

    productos = st.session_state.get("productos")
    movimientos = st.session_state.get("movimientos")
    inventario = st.session_state.get("inventario")

    if productos is not None and movimientos is not None and inventario is not None:

        st.success("✅ Archivos cargados")

        st.session_state.data_ready = True
