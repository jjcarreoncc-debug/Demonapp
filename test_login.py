import streamlit as st
import pandas as pd
import hashlib

from database import get_connection


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


st.title("🧪 Test Base de Datos")

conn = get_connection()

# =====================================
# TABLAS
# =====================================
st.subheader("📋 Tablas existentes")

tablas = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn
)

st.dataframe(
    tablas,
    use_container_width=True
)

# =====================================
# USUARIOS
# =====================================
st.subheader("👥 Usuarios")

try:

    usuarios = pd.read_sql_query(
        """
        SELECT
            id_usuario,
            usuario,
            nombre,
            estado
        FROM usuarios
        """,
        conn
    )

    st.dataframe(
        usuarios,
        use_container_width=True
    )

except Exception as e:

    st.error(
        "No se pudo leer usuarios"
    )

    st.exception(e)

# =====================================
# CREAR ADMIN
# =====================================
st.subheader("🔐 Crear Admin Temporal")

if st.button("Crear usuario admin"):

    cursor = conn.cursor()

    rol_admin = cursor.execute(
        """
        SELECT id_rol
        FROM roles
        WHERE nombre_rol = 'Admin'
        """
    ).fetchone()

    if rol_admin is None:

        st.error(
            "No existe rol Admin"
        )

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

        st.success(
            "✅ Usuario admin creado"
        )

        st.info(
            "Usuario: admin | Password: 1234"
        )

conn.close()
