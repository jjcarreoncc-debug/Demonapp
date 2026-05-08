
import streamlit as st
import base64

st.set_page_config(layout="wide")


def get_base64(imagen):
    with open(imagen, "rb") as f:
        return base64.b64encode(f.read()).decode()


fondo = get_base64("logofondo.JPG")


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

.bloque {{

    background: rgba(255,255,255,0.88);

    width: 430px;

    margin: auto;

    margin-top: 7vh;

    padding: 40px;

    border-radius: 25px;

    box-shadow:
        0 20px 50px rgba(0,0,0,0.25);

    text-align: center;
}}

.titulo {{

    font-size: 38px;

    font-weight: 800;

    color: #0f172a;

    margin-top: 10px;

    margin-bottom: 25px;
}}

.stTextInput input {{

    height: 52px;

    border-radius: 12px;
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


st.markdown(
    '<div class="bloque">',
    unsafe_allow_html=True
)

st.image(
    "LOOGO-TIDS-CONSULTING (2).jpg",
    width=170
)

st.image(
    "logo1.png",
    width=240
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
