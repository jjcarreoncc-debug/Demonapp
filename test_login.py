import streamlit as st
import pandas as pd
import hashlib

from database import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


st.title("🔐 Reset / Validar Admin")

conn = get_connection()
cursor = conn.cursor()

st.subheader("👥 Usuarios actuales")

usuarios = pd.read_sql_query(
    """
    SELECT
        u.id_usuario,
        u.usuario,
        u.nombre,
        u.estado,
        u.password_hash,
        r.nombre_rol AS rol
    FROM usuarios u
    LEFT JOIN roles r
        ON u.id_rol = r.id_rol
    """,
    conn
)

st.dataframe(usuarios, use_container_width=True)

if st.button("Reset admin a 1234"):

    password_nuevo = hash_password("1234")

    cursor.execute(
        """
        UPDATE usuarios
        SET
            password_hash = ?,
            estado = 'Activo'
        WHERE usuario = 'admin'
        """,
        (password_nuevo,)
    )

    conn.commit()

    st.success("✅ Reset ejecutado")
    st.info("Usuario: admin")
    st.info("Password: 1234")

    actualizado = pd.read_sql_query(
        """
        SELECT usuario, estado, password_hash
        FROM usuarios
        WHERE usuario = 'admin'
        """,
        conn
    )

    st.dataframe(actualizado, use_container_width=True)

conn.close()
