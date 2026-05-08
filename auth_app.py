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
       FONDO GENERAL
    ========================= */

    .stApp {
        background:
            radial-gradient(circle at top left, #dbeafe 0%, transparent 35%),
            radial-gradient(circle at bottom right, #dbeafe 0%, transparent 35%),
            linear-gradient(135deg, #f8fafc 0%, #eef4ff 100%);
    }

    header {
        visibility: hidden;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        padding-top: 1rem !important;
        max-width: 1400px !important;
    }

    /* =========================
       LOGIN WRAPPER
    ========================= */

    .login-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 90vh;
    }

    /* =========================
       LOGIN CARD
    ========================= */

    .login-card {
        background: rgba(255,255,255,0.92);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 45px;
        width: 520px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.10);
    }

    /* =========================
       TITULOS
    ========================= */

    .sigem-title {
        font-size: 70px;
        font-weight: 800;
        color: #0f3fae;
        line-height: 1;
        margin-top: 10px;
        margin-bottom: 0px;
    }

    .sigem-subtitle {
        font-size: 18px;
        color: #334155;
        margin-bottom: 35px;
    }

    .login-text {
        font-size: 38px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 5px;
    }

    .login-subtext {
        font-size: 15px;
        color: #64748b;
        margin-bottom: 30px;
    }

    /* =========================
       INPUTS
    ========================= */

    .stTextInput > div > div > input {
        border-radius: 14px;
        height: 52px;
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
        background: linear-gradient(
            90deg,
            #0f3fae 0%,
            #2563eb 100%
        );

        color: white;
        font-size: 20px;
        font-weight: 700;
        border: none;
        margin-top: 15px;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37,99,235,0.30);
        color: white;
    }

    /* =========================
       FOOTER
    ========================= */

    .footer-login {
        text-align: center;
        margin-top: 30px;
        color: #64748b;
        font-size: 14px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="login-wrapper">',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        st.image(
            "logo_tids.png",
            width=180
        )

        st.markdown(
            '<div class="sigem-title">SIGEM</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '''
            <div class="sigem-subtitle">
            Sistema Integrado de Gestión Empresarial
            </div>
            ''',
            unsafe_allow_html=True
        )

        st.image(
            "logo1.png",
            width=260
        )

    with col2:

        st.markdown(
            '<div class="login-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="login-text">Inicio de sesión</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '''
            <div class="login-subtext">
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
