import streamlit as st
import hashlib
import base64

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

    # =========================
    # FONDO BASE64
    # =========================

    with open("logofondo.png", "rb") as f:
        fondo_base64 = base64.b64encode(
            f.read()
        ).decode()

    st.markdown(f"""
    <style>

    /* =========================
       OCULTAR STREAMLIT
    ========================= */

    header {{
        visibility: hidden;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    /* =========================
       FONDO
    ========================= */

    .stApp {{

        background-image:
            url("data:image/png;base64,{fondo_base64}");

        background-size: cover;

        background-position: center;

        background-repeat: no-repeat;

        background-attachment: fixed;
    }}

    /* =========================
       OVERLAY
    ========================= */

    .stApp::before {{

        content: "";

        position: fixed;

        top: 0;
        left: 0;

        width: 100%;
        height: 100%;

        background:
            rgba(255,255,255,0.72);

        backdrop-filter:
            blur(3px);

        z-index: 0;
    }}

    /* =========================
       CONTENIDO
    ========================= */

    .main .block-container {{

        position: relative;

        z-index: 1;

        max-width: 100% !important;

        padding-top: 4vh !important;

        padding-bottom: 0rem !important;
    }}

    /* =========================
       CARD LOGIN
    ========================= */

    .login-card {{

        background:
            rgba(255,255,255,0.96);

        border-radius: 30px;

        padding:
            45px
            50px
            35px
            50px;

        width: 470px;

        margin: auto;

        margin-top: 5vh;

        box-shadow:
            0 20px 50px rgba(0,0,0,0.15);

        border:
            1px solid rgba(255,255,255,0.5);
    }}

    /* =========================
       LOGOS
    ========================= */

    .logo-tids,
    .logo-sigem {{

        display: flex;

        justify-content: center;

        align-items: center;
    }}

    .logo-tids {{
        margin-bottom: 10px;
    }}

    .logo-sigem {{
        margin-bottom: 10px;
    }}

    /* =========================
       TITULOS
    ========================= */

    .login-title {{

        text-align: center;

        font-size: 36px;

        font-weight: 700;

        color: #0f172a;

        margin-top: 10px;

        margin-bottom: 8px;
    }}

    .login-subtitle {{

        text-align: center;

        font-size: 15px;

        color: #64748b;

        margin-bottom: 30px;
    }}

    /* =========================
       INPUTS
    ========================= */

    .stTextInput input {{

        border-radius: 14px !important;

        height: 55px !important;

        border: 1px solid #dbe4f0 !important;

        font-size: 16px !important;

        padding-left: 15px !important;
    }}

    .stTextInput label {{

        font-weight: 600;

        color: #0f172a;
    }}

    /* =========================
       BOTON
    ========================= */

    .stButton button {{

        width: 100%;

        height: 56px;

        border-radius: 14px;

        border: none;

        background:
            linear-gradient(
                90deg,
                #0f3fae 0%,
                #2563eb 100%
            );

        color: white;

        font-size: 18px;

        font-weight: 700;

        margin-top: 15px;

        transition: 0.2s;
    }}

    .stButton button:hover {{

        transform: scale(1.02);

        background:
            linear-gradient(
                90deg,
                #1d4ed8 0%,
                #3b82f6 100%
            );

        color: white;
    }}

    /* =========================
       FOOTER
    ========================= */

    .footer-login {{

        text-align: center;

        margin-top: 25px;

        color: #64748b;

        font-size: 14px;
    }}

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
        width=170
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
        width=230
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
