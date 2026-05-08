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

    /* Fondo general */
    .stApp {
        background: #f4f6f8 !important;
    }

    /* Contenedor principal */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
        max-width: 430px !important;
    }

    /* Ocultar header */
    header {
        visibility: hidden;
    }

    /* Card login */
    .login-card {
        background: white;
        padding: 35px;
        border-radius: 22px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        margin-top: 20px;
    }

    /* Logo */
    .logo-container {
        text-align: center;
        margin-bottom: 10px;
    }

    /* Título */
    .login-title {
        font-size: 32px;
        font-weight: 800;
        color: #24364b;
        margin-top: 10px;
        margin-bottom: 5px;
        text-align: center;
    }

    /* Subtitulo */
    .login-subtitle {
        font-size: 14px;
        color: #7b8794;
        margin-bottom: 25px;
        text-align: center;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 10px;
    }

    /* Botón */
    div.stButton > button {
        width: 100%;
        height: 46px;
        border-radius: 12px;
        background-color: #1f5f7a;
        color: white;
        font-weight: 700;
        border: none;
    }

    /* Hover botón */
    div.stButton > button:hover {
        background-color: #17495e;
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    try:

        st.markdown(
            '<div class="logo-container">',
            unsafe_allow_html=True
        )

        st.image(
            "LOOGO-TIDS-CONSULTING (2).jpg",
            width=180
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    except Exception:
        st.markdown("### 🔐")

    st.markdown(
        '<div class="login-title">Inicio de sesión</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Ingresa tus credenciales para continuar</div>',
        unsafe_allow_html=True
    )

    usuario = st.text_input("Usuario")

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    if st.button("Ingresar"):

        resultado = validar_login(
            usuario.strip(),
            password.strip()
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

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


def logout_app():

    if st.sidebar.button("🚪 Cerrar sesión"):

        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.nombre = None
        st.session_state.rol = None

        st.rerun()
