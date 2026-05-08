import streamlit as st
import hashlib
import base64
from pathlib import Path

from database import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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

    password_bd = str(row["password_hash"]).strip()

password_ingresado = str(password).strip()

password_hash = hash_password(
    password_ingresado
)

if (
    password_bd != password_ingresado
    and
    password_bd != password_hash
):
    return None
        
def get_base64_image(image_path):

    file_path = Path(image_path)

    if not file_path.exists():
        return None

    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def login_app():

    bg_image = get_base64_image("logofondo.JPG")
    sigem_logo = get_base64_image("logo1.png")

    if bg_image:
        fondo_css = f"""
        background-image:
            linear-gradient(
                rgba(0,0,0,0.45),
                rgba(0,0,0,0.45)
            ),
            url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        """
    else:
        fondo_css = "background-color: #0f172a;"

    st.markdown(f"""
    <style>

    header, #MainMenu, footer {{
        visibility: hidden;
    }}

    .stApp {{
        {fondo_css}
    }}

    .block-container {{
        padding-top: 6vh !important;
        max-width: 100% !important;
    }}

    .login-card {{
        background: rgba(15,23,42,0.68);
        border-radius: 30px;
        padding: 35px 50px 35px 50px;
        width: 500px;
        margin: auto;
        margin-top: 2vh;
        box-shadow: 0 20px 60px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.14);
        backdrop-filter: blur(6px);
    }}

    .logo-sigem {{
        text-align: center;
        margin-bottom: -5px;
    }}

    .login-title {{
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: white;
        margin-top: 5px;
        margin-bottom: 5px;
        text-shadow: 0 5px 20px rgba(0,0,0,0.40);
    }}

    .login-subtitle {{
        text-align: center;
        font-size: 18px;
        color: white;
        margin-bottom: 30px;
        text-shadow: 0 5px 20px rgba(0,0,0,0.40);
    }}

    .stTextInput > div > div > input {{
        border-radius: 14px;
        height: 55px;
        border: 1px solid rgba(255,255,255,0.18);
        background: rgba(0,0,0,0.38);
        color: white;
        font-size: 16px;
        padding-left: 15px;
    }}

    .stTextInput > label {{
        font-weight: 600;
        color: white !important;
    }}

    div.stButton > button {{
        width: 100%;
        height: 56px;
        border-radius: 14px;
        background: linear-gradient(90deg, #0f3fae 0%, #2563eb 100%);
        color: white !important;
        font-size: 20px;
        font-weight: 700;
        border: none;
        margin-top: 15px;
    }}

    div.stButton > button:hover {{
        background: linear-gradient(90deg, #1d4ed8 0%, #3b82f6 100%);
        color: white !important;
    }}

    .footer-login {{
        text-align: center;
        margin-top: 25px;
        color: rgba(255,255,255,0.78);
        font-size: 14px;
    }}

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    if sigem_logo:
        st.markdown(
            f'''
            <div class="logo-sigem">
                <img src="data:image/png;base64,{sigem_logo}" width="300">
            </div>
            ''',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="login-title">SIGEM</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="login-title">Inicio de sesión</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '''
        <div class="login-subtitle">
        Sistema de Gestión Empresarial
        </div>
        ''',
        unsafe_allow_html=True
    )

    usuario = st.text_input("Usuario", key="login_usuario")

    password = st.text_input(
        "Contraseña",
        type="password",
        key="login_password"
    )

    if st.button("Ingresar", key="btn_login_sigem"):

        resultado = validar_login(
            usuario.strip(),
            password.strip()
        )

        if resultado == "INACTIVO":
            st.warning("⛔ Usuario inactivo")

        elif resultado is None:
            st.error("❌ Usuario o contraseña incorrectos")

        else:
            st.session_state.autenticado = True
            st.session_state.usuario = resultado["usuario"]
            st.session_state.nombre = resultado["nombre"]
            st.session_state.rol = resultado["rol"]

            st.rerun()

    st.markdown(
        '''
        <div class="footer-login">
        © 2026 SIGEM
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


def logout_app():

    if st.sidebar.button("🚪 Cerrar sesión", key="btn_logout_sigem"):

        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.nombre = None
        st.session_state.rol = None

        st.rerun()
