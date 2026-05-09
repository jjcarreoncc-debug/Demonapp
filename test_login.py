import streamlit as st
import hashlib

from database import get_connection


# =====================================
# HASH PASSWORD
# =====================================
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =====================================
# UI
# =====================================
st.title("🔐 Crear Usuario Temporal")


if st.button("Crear Admin Temporal"):

    conn = get_connection()

    cursor = conn.cursor()

    # =====================================
    # BUSCAR ROL ADMIN
    # =====================================
    rol_admin = cursor.execute(
        """
        SELECT id_rol
        FROM roles
        WHERE nombre_rol = 'Admin'
        """
    ).fetchone()

    # =====================================
    # VALIDAR ROL
    # =====================================
    if rol_admin is None:

        st.error(
            "❌ No existe el rol Admin"
        )

    else:

        # =====================================
        # INSERTAR USUARIO
        # =====================================
        cursor.execute(
            """
            INSERT INTO usuarios (

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
            "✅ Usuario temporal creado"
        )

        st.info(
            "Usuario: admin"
        )

        st.info(
            "Password: 1234"
        )

    conn.close()
