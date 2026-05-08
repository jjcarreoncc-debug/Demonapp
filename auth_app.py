import streamlit as st
import base64


st.set_page_config(
    page_title="Prueba Login SIGEM",
    layout="wide"
)


def cargar_imagen_base64(ruta):
    with open(ruta, "rb") as archivo:
        return base64.b64encode(archivo.read()).decode()


fondo = cargar_imagen_base64("logofondo.png")


st.markdown(f"""
<style>

header, footer, #MainMenu {{
    visibility: hidden;
}}

.stApp {{
    background-image: url("data:image/png;base64,{fondo}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

.contenedor {{
    width: 420px;
    margin: auto;
    margin-top: 12vh;
    padding: 40px;
    background: rgba(255, 255, 255, 0.88);
    border-radius: 28px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.20);
    text-align: center;
}}

.titulo {{
    font-size: 34px;
    font-weight: 800;
    color: #0f172a;
    margin-top: 20px;
}}

.subtitulo {{
    font-size: 15px;
    color: #64748b;
    margin-bottom: 25px;
}}

</style>
""", unsafe_allow_html=True)


st.markdown('<div class="contenedor">', unsafe_allow_html=True)

st.image("LOOGO-TIDS-CONSULTING (2).jpg", width=170)

st.image("logo1.png", width=240)

st.markdown('<div class="titulo">Inicio de sesión</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitulo">Prueba visual de fondo, empresa y sistema</div>',
    unsafe_allow_html=True
)

st.text_input("Usuario")

st.text_input("Contraseña", type="password")

st.button("Ingresar")

st.markdown('</div>', unsafe_allow_html=True)
