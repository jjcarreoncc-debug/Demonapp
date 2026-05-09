    import streamlit as st
import hashlib
import base64

from pathlib import Path

from database import get_connection



# =====================================
# HASH PASSWORD
# =====================================
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =====================================
# VALIDAR LOGIN
# =====================================
def validar_login(usuario, password):

    st.write(
        "DEBUG usuario ingresado:",
        usuario
    )

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

    st.write(
        "DEBUG row BD:",
        row
    )

    conn.close()

    # =====================================
    # USUARIO NO EXISTE
    # =====================================
    if row is None:

        st.write(
            "❌ Usuario NO encontrado"
        )

        return None

    # =====================================
    # ESTADO
    # =====================================
    st.write(
        "DEBUG estado:",
        row["estado"]
    )

    if row["estado"] != "Activo":

        st.write(
            "⛔ Usuario inactivo"
        )

        return "INACTIVO"

    # =====================================
    # PASSWORDS
    # =====================================
    password_bd = str(
        row["password_hash"]
    ).strip()

    password_ingresado = str(
        password
    ).strip()

    password_hash = hash_password(
        password_ingresado
    )

    st.write(
        "DEBUG password BD:",
        password_bd
    )

    st.write(
        "DEBUG password ingresado:",
        password_ingresado
    )

    st.write(
        "DEBUG hash ingresado:",
        password_hash
    )

    # =====================================
    # VALIDAR PASSWORD
    # =====================================
    if (
        password_bd != password_ingresado
        and
        password_bd != password_hash
    ):

        st.write(
            "❌ Password incorrecto"
        )

        return None

    # =====================================
    # LOGIN OK
    # =====================================
    st.write(
        "✅ LOGIN CORRECTO"
    )

    return row


# =====================================
# IMAGEN BASE64
# =====================================
def get_base64_image(image_path):

    file_path = Path(image_path)

    if not file_path.exists():

        return None

    with open(file_path, "rb") as img_file:

        return base64.b64encode(
            img_file.read()
        ).decode()


# =====================================
# LOGIN APP
# =====================================
def login_app():

    bg_image = get_base64_image(
        "logofondo.JPG"
    )

    sigem_logo = get_base64_image(
        "logo1.png"
    )

    tids_logo = get_base64_image(
        "LOOGO-TIDS-CONSULTING (2).jpg"
    )

    if bg_image:

        fondo_css = f'''
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
        '''

    else:

        fondo_css = (
            "background-color: #0f172a;"
        )

    st.markdown(f"""
    <style>

    header,
    #MainMenu,
    footer {{
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
        padding: 35px 50px 35px 50px;
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

    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="top-logos">

        <div>
            {
                '<img src="data:image/jpg;base64,' + tids_logo + '" width="190">'
                if tids_logo
                else ''
            }
        </div>

        <div>
            {
                '<img src="data:image/png;base64,' + sigem_logo + '" width="190">'
                if sigem_logo
                else '<span style="color:white;font-size:28px;font-weight:800;">SIGEM</span>'
            }
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="login-card">',
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

    usuario = st.text_input(
        "Usuario",
        key="login_usuario"
    )

    password = st.text_input(
        "Contraseña",
        type="password",
        key="login_password"
    )

    # =====================================
    # LOGIN BUTTON
    # =====================================
    if st.button(
        "Ingresar",
        key="btn_login_sigem"
    ):

        resultado = validar_login(
            usuario.strip(),
            password.strip()
        )

        st.write(
            "DEBUG resultado:",
            resultado
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

            st.write(
                "✅ SESSION OK"
            )

            st.session_state.autenticado = True

            st.session_state.usuario = (
                resultado["usuario"]
            )

            st.session_state.nombre = (
                resultado["nombre"]
            )

            st.session_state.rol = (
                resultado["rol"]
            )

            st.write(
                "DEBUG session:",
                st.session_state
            )

            st.rerun()

    st.markdown(
        '''
        <div class="footer-login">
            © 2026 SIGEM
        </div>
        ''',
        unsafe_allow_html=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =====================================
# LOGOUT
# =====================================
def logout_app():

    if st.sidebar.button(
        "🚪 Cerrar sesión",
        key="btn_logout_sigem_unico"
    ):

        st.session_state.autenticado = False

        st.session_state.usuario = None

        st.session_state.nombre = None

        st.session_state.rol = None

        st.rerun()
