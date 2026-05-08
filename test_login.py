
import streamlit as st
import base64

st.set_page_config(layout="wide")


def get_base64(imagen):
    with open(imagen, "rb") as f:
        return base64.b64encode(f.read()).decode()


fondo = get_base64("logofondo.png")


st.markdown(f"""
<style>

header, #MainMenu, footer {{
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
        rgba(0,0,0,0.35);

    z-index: 0;
}}

.main .block-container {{

    position: relative;

    z-index: 1;

    padding-top: 8vh;
}}

.element-container:has(style) {{
    display: none;
}}

.login-box {{

    background:
        rgba(255,255,255,0.92);

    padding: 45px;

    border-radius: 24px;

    box-shadow:
        0 20px 60px rgba(0,0,0,0.35);
}}

.logo-empresa {{

    display: flex;

    justify-content: center;

    margin-bottom: 10px;
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

    color: #0f172a;

    margin-bottom: 30px;
}}

.stTextInput input {{

    height: 52px;

    border-radius: 12px;

    border: none;
}}

.stButton button {{

    width: 100%;

    height: 52px;

    border-radius: 12px;

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


izq, centro, der = st.columns([1,1,1])

with centro:

    st.markdown(
        '<div class="login-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="logo-empresa">',
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
        '<div class="titulo">Inicio de sesión</div>',
        unsafe_allow_html=True
    )

    st.text_input("Usuario")

    st.text_input(
        "Contraseña",
        type="password"
    )

    st.button("Ingresar")

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )
