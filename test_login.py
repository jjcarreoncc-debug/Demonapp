import streamlit as st
import base64

st.set_page_config(
    page_title="SIGEM",
    layout="wide"
)


def get_base64(imagen):

    with open(imagen, "rb") as f:

        return base64.b64encode(
            f.read()
        ).decode()


# =========================
# IMAGENES
# =========================

fondo = get_base64("logofondo.JPG")

sigem = get_base64("logo1.png")


# =========================
# CSS
# =========================

st.markdown(f"""
<style>

header,
#MainMenu,
footer {{
    visibility: hidden;
}}

.stApp {{

    background-image:
        url("data:image/png;base64,{fondo}");

    background-size: cover;

    background-position: center;

    background-repeat: no-repeat;

    background-attachment: fixed;
}}

.stApp::before {{

    content: "";

    position: fixed;

    inset: 0;

    background:
        rgba(0,0,0,0.45);

    z-index: 0;
}}

.main .block-container {{

    position: relative;

    z-index: 1;

    padding-top: 10vh;
}}

.logo-sigem {{

    display: flex;

    justify-content: center;

    margin-bottom: 20px;
}}

.titulo {{

    text-align: center;

    font-size: 42px;

    font-weight: 800;

    color: white;

    margin-bottom: 10px;

    text-shadow:
        0 4px 15px rgba(0,0,0,0.4);
}}

.subtitulo {{

    text-align: center;

    font-size: 18px;

    color: white;

    margin-bottom: 35px;

    text-shadow:
        0 4px 15px rgba(0,0,0,0.4);
}}

.stTextInput input {{

    height: 55px;

    border-radius: 14px;

    border: none;

    background:
        rgba(255,255,255,0.92);

    font-size: 16px;
}}

.stButton button {{

    width: 100%;

    height: 55px;

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
}}

</style>
""", unsafe_allow_html=True)


# =========================
# COLUMNAS
# =========================

izq, centro, der = st.columns([1,1,1])


# =========================
# LOGIN
# =========================

with centro:

    st.markdown(f"""
    <div class="logo-sigem">
        <img src="data:image/png;base64,{sigem}" width="260">
    </div>

    <div class="titulo">
        Inicio de sesión
    </div>

    <div class="subtitulo">
        Sistema de Gestión Empresarial
    </div>
    """, unsafe_allow_html=True)

    st.text_input("Usuario")

    st.text_input(
        "Contraseña",
        type="password"
    )

    st.button("Ingresar")
