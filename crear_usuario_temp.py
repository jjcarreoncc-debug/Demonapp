import streamlit as st
import pandas as pd

from database import get_connection

st.title("Crear usuario temporal")

conn = get_connection()

st.subheader("Tablas en la base de datos")

tablas = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table'",
    conn
)

st.dataframe(tablas)

st.subheader("Crear usuario temporal")

usuario = st.text_input("Usuario", "admin_temp")
nombre = st.text_input("Nombre", "Administrador Temporal")
password = st.text_input("Contraseña", "1234")
estado = st.selectbox("Estado", ["Activo", "Inactivo"])

if st.button("Crear usuario"):
    try:
        conn.execute(
            """
            INSERT INTO usuarios (
                usuario,
                nombre,
                password_hash,
                estado
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                usuario,
                nombre,
                password,
                estado
            )
        )

        conn.commit()
        st.success("Usuario creado correctamente")

    except Exception as e:
        st.error(f"Error: {e}")

st.subheader("Usuarios actuales")

try:
    usuarios = pd.read_sql("SELECT * FROM usuarios", conn)
    st.dataframe(usuarios)
except Exception as e:
    st.error(f"No pude leer usuarios: {e}")

conn.close()
