import streamlit as st
import hashlib
import base64
import sqlite3
from pathlib import Path

from inventarios_app import inventarios_app
from carga_app import carga_app
from compras_app import compras_app
from logistica_app import logistica_app
from wms_app import wms_app
from mantenimiento_app import mantenimiento_app
from menu_dinamico import sidebar_dinamico


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "erp.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_base64_image(image_path):
    file_path = BASE_DIR / image_path

    if not file_path.exists():
        return None

    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def validar_login(usuario, password):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
        WHERE UPPER(u.usuario) = UPPER(?)
        """,
        (usuario.strip(),)
    ).fetchone()

    conn.close()

    if row is None:
        return None

    password_bd = str(row["password_hash"]).strip()
    password_ingresado = str(password).strip()
    password_hash = hash_password(password_ingresado)

    if password_bd != password_ingresado and password_bd != password_hash:
        return None

    return row


def login_app():
    bg_image = get_base64_image("logofondo.JPG")
    sigem_logo = get_base64_image("logo1.png")
    tids_logo = get_base64_image("LOOGO-TIDS-CONSULTING (2).jpg")

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
        padding-top: 2vh !important;
        max-width: 100% !important;
    }}

    .top-logos {{
        width: 94%;
        margin: 0 auto 20px auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    .top-logos img {{
        object-fit: contain;
    }}

    .login-card {{
        background: rgba(15,23,42,0.68);
        border-radius: 30px;
        padding: 35px 50px;
        width: 500px;
        max-width: 90%;
        margin: auto;
        margin-top: 2vh;
        box-shadow: 0 20px 60px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.14);
        backdrop-filter: blur(6px);
    }}

    .login-title {{
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: white;
        margin-top: 5px;
        margin-bottom: 5px;
    }}

    .login-subtitle {{
        text-align: center;
        font-size: 18px;
        color: white;
        margin-bottom: 30px;
    }}

    .stTextInput {{
        max-width: 420px;
        margin: auto;
    }}

    .stButton {{
        max-width: 420px;
        margin: auto;
    }}

    .stTextInput > div > div > input {{
        border-radius: 14px;
        height: 55px;
        background: rgba(0,0,0,0.38);
        color: white;
        font-size: 16px;
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

    .footer-login {{
        text-align: center;
        margin-top: 25px;
        color: rgba(255,255,255,0.78);
        font-size: 14px;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="top-logos">
        <div>
            {'<img src="data:image/jpg;base64,' + tids_logo + '" width="190">' if tids_logo else ''}
        </div>
        <div>
            {'<img src="data:image/png;base64,' + sigem_logo + '" width="190">' if sigem_logo else '<span style="color:white;font-size:28px;font-weight:800;">SIGEM</span>'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="login-title">Inicio de sesión</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">Sistema de Gestión Empresarial</div>',
        unsafe_allow_html=True
    )

    usuario = st.text_input("Usuario", key="login_usuario")

    password = st.text_input(
        "Contraseña",
        type="password",
        key="login_password"
    )

    if st.button("Ingresar", key="btn_login_sigem"):
        resultado = validar_login(usuario, password)

        if resultado is None:
            st.error("❌ Usuario o contraseña incorrectos")
        else:
            st.session_state.autenticado = True
            st.session_state.usuario = resultado["usuario"]
            st.session_state.nombre = resultado["nombre"]
            st.session_state.rol = resultado["rol"]

            st.success("✅ Login correcto")
            st.rerun()

    st.markdown(
        '<div class="footer-login">© 2026 SIGEM</div>',
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


def logout_app():
    if st.sidebar.button("🚪 Cerrar sesión", key="btn_logout_sigem_unico"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.nombre = None
        st.session_state.rol = None
        st.rerun()


if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "rol" not in st.session_state:
    st.session_state.rol = None

if not st.session_state.autenticado:
    login_app()
    st.stop()

logout_app()

ruta = sidebar_dinamico()

if ruta == "inicio":
    st.empty()

elif ruta == "inventarios":
    st.title("📦 Inventarios")
    inventarios_app()

elif ruta == "compras":
    st.title("🛒 Compras")
    compras_app()

elif ruta == "logistica":
    st.title("🚚 Logística")
    logistica_app()

elif ruta == "wms":
    st.title("🏬 WMS")
    wms_app()

elif ruta == "mantenimiento":
    st.title("🛠️ Mantenimiento")
    mantenimiento_app()

else:
    st.warning(f"Ruta no configurada: {ruta}")
