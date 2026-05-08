import streamlit as st
import sqlite3
import pandas as pd

from database import get_connection

st.title("Crear usuario temporal")

conn = get_connection()

st.subheader("Roles existentes")
roles = pd.read_sql("SELECT * FROM roles", conn)
st.dataframe(roles)

st.subheader("Crear usuario")

usuario = st.text_input("Usuario", "admin_temp")
nombre = st.text_input("Nombre", "Administrador Temporal")
password = st.text_input("Contraseña", "1234")
estado = st.selectbox("Estado", ["Activo", "Inactivo"])
id_rol = st.number_input("ID Rol", min_value=1, step=1, value=1)

if st.button("Crear usuario"):
    try:
        conn.execute(
            """
            INSERT INTO usuarios (
                usuario,
                nombre,
                password_hash,
                estado,
                id_rol
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                usuario,
                nombre,
                password,
                estado,
                id_rol
            )
        )

        conn.commit()
        st.success("Usuario creado correctamente")

    except Exception as e:
        st.error(f"Error: {e}")

st.subheader("Usuarios actuales")
usuarios = pd.read_sql(
    """
    SELECT
        u.id_usuario,
        u.usuario,
        u.nombre,
        u.estado,
        u.id_rol,
        r.nombre_rol
    FROM usuarios u
    LEFT JOIN roles r
        ON u.id_rol = r.id_rol
    """,
    conn
)
st.dataframe(usuarios)

conn.close()
