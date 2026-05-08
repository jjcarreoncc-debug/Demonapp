import streamlit as st
import pandas as pd

from database import get_connection


st.title("Inicializar sistema de usuarios")

conn = get_connection()


if st.button("Crear tablas y usuario admin"):
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            nombre TEXT,
            password_hash TEXT,
            estado TEXT,
            id_rol INTEGER,
            FOREIGN KEY (id_rol)
                REFERENCES roles(id_rol)
        )
        """)

        conn.execute("""
        INSERT OR IGNORE INTO roles (
            id_rol,
            nombre_rol
        )
        VALUES (
            1,
            'Admin'
        )
        """)

        conn.execute("DELETE FROM usuarios WHERE usuario = 'admin'")

        conn.execute("""
        INSERT INTO usuarios (
            usuario,
            nombre,
            password_hash,
            estado,
            id_rol
        )
        VALUES (
            'admin',
            'Administrador',
            '1234',
            'Activo',
            1
        )
        """)

        conn.commit()
        st.success("Admin creado/forzado correctamente")

    except Exception as e:
        st.error(f"Error: {e}")


st.subheader("Usuarios creados")
try:
    usuarios = pd.read_sql("SELECT * FROM usuarios", conn)
    st.dataframe(usuarios)
except Exception as e:
    st.error(f"No pude leer usuarios: {e}")


st.subheader("Roles creados")
try:
    roles = pd.read_sql("SELECT * FROM roles", conn)
    st.dataframe(roles)
except Exception as e:
    st.error(f"No pude leer roles: {e}")


conn.close()
