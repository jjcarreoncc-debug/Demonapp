import streamlit as st
import hashlib

from database import get_connection


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def validar_login(usuario, password):
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute(
        """
        SELECT
            u.usuario,
            u.nombre,
            u.password_hash,
            u.estado,
            r.nombre_rol AS rol
        FROM usuarios u
        LEFT JOIN roles r
            ON u.id_rol = r.id_rol
        WHERE u.usuario = ?
        """,
        (usuario,)
    ).fetchone()

    conn.close()

    if row is None:
        return None

    if row["estado"] != "Activo":
        return "INACTIVO"

    if row["password_hash"] != password:
        return None

    return row


def login_app():
    st.markdown("""
    <style>
    .stApp {
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🔐 Login")

    usuario = st.text_input("Usuario")
    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Ingresar"):
        resultado = validar_login(
            usuario,
            password
        )

        if resultado == "INACTIVO":
            st.warning(
                "⛔ Usuario inactivo. Contacta al administrador."
            )

        elif resultado is None:
            st.error(
                "❌ Usuario o contraseña incorrectos."
            )

        else:
            st.session_state.autenticado = True
            st.session_state.usuario = resultado["usuario"]
            st.session_state.nombre = resultado["nombre"]
            st.session_state.rol = resultado["rol"]

            st.rerun()


def logout_app():
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.nombre = None
        st.session_state.rol = None

        st.rerun()
