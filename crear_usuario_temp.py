import streamlit as st

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

        # Crear rol admin
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

        # Crear usuario admin
        conn.execute("""
        INSERT OR IGNORE INTO usuarios (
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

        st.success("Sistema inicializado correctamente")

    except Exception as e:

        st.error(f"Error: {e}")

conn.close()
