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

    /* =========================
       OCULTAR STREAMLIT
    ========================= */

    header {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* =========================
       FONDO
    ========================= */

    .stApp {

        background-image:
            linear-gradient(
                rgba(255,255,255,0.84),
                rgba(255,255,255,0.84)
            ),
            url("logofondo.JPG");

        background-size: cover;

        background-position: center;

        background-repeat: no-repeat;

        background-attachment: fixed;
    }

    .block-container {
        padding-top: 0rem !important;
        max-width: 100% !important;
    }

    /* =========================
       CARD LOGIN
    ========================= */

    .login-card {

        background: rgba(255,255,255,0.94);

        border-radius: 30px;

        padding:
            45px
            50px
            35px
            50px;

        width: 520px;

        margin:
            auto;

        margin-top:
            8vh;

        box-shadow:
            0 15px 40px rgba(0,0,0,0.10);

        border:
            1px solid #dbe4f0;
    }

    /* =========================
       LOGOS
    ========================= */

    .logo-tids {
        text-align: center;
        margin-bottom: 10px;
    }

    .logo-sigem {
        text-align: center;
        margin-bottom: 10px;
    }

    /* =========================
       TITULOS
    ========================= */

    .login-title {

        text-align: center;

        font-size: 34px;

        font-weight: 700;

        color: #0f172a;

        margin-top: 15px;

        margin-bottom: 5px;
    }

    .login-subtitle {

        text-align: center;

        font-size: 15px;

        color: #64748b;

        margin-bottom: 30px;
    }

    /* =========================
       INPUTS
    ========================= */

    .stTextInput > div > div > input {

        border-radius: 14px;

        height: 55px;

        border: 1px solid #dbe4f0;

        font-size: 16px;

        padding-left: 15px;
    }

    .stTextInput > label {

        font-weight: 600;

        color: #0f172a;
    }

    /* =========================
       BOTON
    ========================= */

    div.stButton > button {

        width: 100%;

        height: 56px;

        border-radius: 14px;

        background:
            linear-gradient(
                90deg,
                #0f3fae 0%,
                #2563eb 100%
            );

        color: white;

        font-size: 20px;

        font-weight: 700;

        border: none;

        margin-top: 15px;
    }

    div.stButton > button:hover {

        background:
            linear-gradient(
                90deg,
                #1d4ed8 0%,
                #3b82f6 100%
            );

        color: white;
    }

    /* =========================
       FOOTER
    ========================= */

    .footer-login {

        text-align: center;

        margin-top: 25px;

        color: #64748b;

        font-size: 14px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="login-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="logo-tids">',
        unsafe_allow_html=True
    )

    st.image(
        "LOOGO-TIDS-CONSULTING (2).jpg",
        width=140
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="logo-sigem">',
        unsafe_allow_html=True
    )

    st.image(
        "logo1.png",
        width=260
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-title">Inicio de sesión</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="login-subtitle">
        Ingresa tus credenciales para continuar
        </div>
        ''',
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
                "⛔ Usuario inactivo"
            )

        elif resultado is None:

            st.error(
                "❌ Usuario o contraseña incorrectos"
            )

        else:

            st.session_state.autenticado = True
            st.session_state.usuario = resultado["usuario"]
            st.session_state.nombre = resultado["nombre"]
            st.session_state.rol = resultado["rol"]

            st.rerun()

    st.markdown(
        '''
        <div class="footer-login">
        © 2026 SIGEM | Desarrollado por TIDS Consulting
        </div>
        ''',
        unsafe_allow_html=True
    )

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
