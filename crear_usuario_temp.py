import streamlit as st
import pandas as pd

from database import get_connection

st.title("Cambiar rol usuario")

conn = get_connection()

usuarios = pd.read_sql(
    "SELECT * FROM usuarios",
    conn
)

st.dataframe(usuarios)

usuario = st.text_input("Usuario a convertir en Admin")

if st.button("Dar permisos Admin"):

    try:

        conn.execute("""
        UPDATE usuarios
        SET id_rol = 1
        WHERE usuario = ?
        """, (usuario,))

        conn.commit()

        st.success("Rol actualizado correctamente")

    except Exception as e:

        st.error(f"Error: {e}")

conn.close()
