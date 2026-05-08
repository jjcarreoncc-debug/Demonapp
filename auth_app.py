import streamlit as st
import base64


def get_base64(imagen):
    with open(imagen, "rb") as f:
        return base64.b64encode(f.read()).decode()


def login_app():

    fondo = get_base64("logofondo.JPG")
    sigem = get_base64("logo1.png")

    st.markdown(f"""
    <style>
    header, #MainMenu, footer {{
        visibility: hidden;
    }}

    .stApp {{
        background-image: url("data:image/jpeg;base64,{fondo}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.45);
        z-index: 0;
    }}

    .main .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 8vh;
        max-width: 1000px;
    }}

    .logo-sigem {{
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
    }}

    .titulo {{
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
        text-shadow: 0 5px 20px rgba(0,0,0,0.40);
    }}

    .subtitulo {{
        text-align: center;
        font-size: 22px;
        color: white;
        margin-bottom: 45px;
        text-shadow: 0 5px 20px rgba(0,0,0,0.40);
    }}

    .stTextInput input {{
        height: 58px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.25);
        background: rgba(0,0,0,0.45);
        color: white;
        font-size: 18px;
    }}

    .stTextInput label {{
        color: white !important;
        font-size: 15px;
        font-weight: 600;
    }}

    .stButton button {{
        width: 100%;
        height: 58px;
        border-radius: 14px;
        border: none;
        background: linear-gradient(90deg,#0f3fae 0%,#2563eb 100%);
        color: white;
        font-size: 22px;
        font-weight: 700;
        margin-top: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

    izq, centro, der = st.columns([1, 1, 1])

    with centro:
        st.markdown(f"""
        <div class="logo-sigem">
            <img src="data:image/png;base64,{sigem}" width="320">
        </div>

        <div class="titulo">
            INICIO DE SESIÓN
        </div>

        <div class="subtitulo">
            Sistema de Gestión Empresarial
        </div>
        """, unsafe_allow_html=True)

        usuario = st.text_input("Usuario")

        password = st.text_input(
            "Contraseña",
            type="password"
        )

        if st.button("INGRESAR"):

            if usuario == "admin" and password == "1234":
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.session_state.nombre = "Administrador"
                st.session_state.rol = "Admin"
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")


def logout_app():
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.nombre = None
        st.session_state.rol = None
        st.rerun()
