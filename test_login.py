import streamlit as st
import pandas as pd
import hashlib

from database import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


st.title("🔐 Test crear admin")

conn = get_connection()
cursor = conn.cursor()

st.subheader("📋 Roles actuales")
roles_df = pd.read_sql_query("SELECT * FROM roles", conn)
st.dataframe(roles_df, use_container_width=True)

st.subheader("👥 Usuarios actuales")
usuarios_df = pd.read_sql_query(
    "SELECT id_usuario, usuario, nombre, estado, id_rol FROM usuarios",
    conn
)
st.dataframe(usuarios_df, use_container_width=True)

if st.button("Crear admin 1234"):

    rol_admin = cursor.execute(
        "SELECT id_rol FROM roles WHERE nombre_rol = ?",
        ("Admin",)
    ).fetchone()

    if rol_admin is None:
        st.error("❌ No existe rol Admin")
    else:
        cursor.execute(
            """
            INSERT OR REPLACE INTO usuarios (
                usuario,
                nombre,
                email,
                password_hash,
                id_rol,
                estado,
                modulo_inicial
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "admin",
                "Administrador",
                "admin@sigem.com",
                hash_password("1234"),
                rol_admin["id_rol"],
                "Activo",
                "Inicio"
            )
        )

        conn.commit()

        st.success("✅ Admin creado: admin / 1234")
        st.rerun()

conn.close()
