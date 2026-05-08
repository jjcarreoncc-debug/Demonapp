import streamlit as st
import base64

# ======================================
# CONFIGURACION PAGINA
# ======================================

st.set_page_config(
    page_title="SIGEM",
    layout="wide"
)

# ======================================
# FUNCION BASE64
# ======================================

def get_base64(imagen):

    with open(imagen, "rb") as f:

        return base64.b64encode(
            f.read()
        ).decode()


# ======================================
# IMAGENES
# ======================================

fondo = get_base64("logofondo.png")

sigem = get_base64("logo1.png")


# ======================================
# CSS
# ======================================

st.markdown(f"""
<style>

/* ======================================
   OCULTAR STREAMLIT
====================================== */

header,
#MainMenu,
footer {{
    visibility: hidden;
}}

/* ======================================
   FONDO
====================================== */

.stApp {{

    background-image:
        url("data:image/png;base64,{fondo}");

    background-size: cover;

    background-position: center;

    background-repeat: no-repeat;

    background-attachment: fixed;
}}

/* ======================================
   OVERLAY OSCURO
====================================== */

.stApp::before {{

    content: "";

    position: fixed;

    inset: 0;

    background:
        rgba(0,0,0,0.45);

    z-index: 0;
}}

/* ======================================
   CONTENIDO
====================================== */

.main .block-container {{

    position: relative;

    z-index: 1;

    padding-top: 8vh;

    max-width: 1000px;
}}

/* ======================================
   LOGO
====================================== */

.logo-sigem {{

    display: flex;

    justify-content: center;

    margin-bottom: 15px;
}}

/* ======================================
   TITULOS
====================================== */

.titulo {{

    text-align: center;

    font-size: 52px;

    font-weight: 800;

    color: white;

    margin-bottom: 10px;

    text-shadow:
        0 5px 20px rgba(0,0,0,0.40);
}}

.subtitulo {{

    text-align: center;

    font-size: 22px;

    color: white;

    margin-bottom: 45px;

    text-shadow:
        0 5px 20px rgba(0,0,0,0.40);
}}

/* ======================================
   INPUTS
====================================== */

.stTextInput input {{

    height: 58px;

    border-radius: 14px;

    border:
        1px solid rgba(255,255,255,0.25);

    background:
        rgba(0,0,0,0.45);

    color: white;

    font-size: 18px;

    backdrop-filter: blur(5px);
}}

.stTextInput label {{

    color: white !important;

    font-size: 15px;

    font-weight: 600;
}}

/* ======================================
   BOTON
====================================== */

.stButton button {{

    width: 100%;

    height: 58px;

    border-radius: 14px;

    border: none;

    background:
        linear-gradient(
            90deg,
            #0f3fae 0%,
            #2563eb 100%
        );

    color: white;

    font-size: 22px;

    font-weight: 700;

    margin-top: 15px;

    transition: 0.2s;
}}

.stButton button:hover {{

    transform: scale(1.01);

    background:
        linear-gradient(
            90deg,
            #2563eb 0%,
            #3b82f6 100%
        );
}}

</style>
""", unsafe_allow_html=True)


# ======================================
# CENTRAR LOGIN
# ======================================

izq, centro, der = st.columns([1,1,1])

with centro:

    # ======================================
    # LOGO
    # ======================================

    st.markdown(f"""
    <div class="logo-sigem">
        <img src="data:image/png;base64,{sigem}" width="320">
    </div>
    """, unsafe_allow_html=True)

    # ======================================
    # TITULOS
    # ======================================

    st.markdown("""
    <div class="titulo">
        INICIO DE SESIÓN
    </div>

    <div class="subtitulo">
        Sistema de Gestión Empresarial
    </div>
    """, unsafe_allow_html=True)

    # ======================================
    # FORMULARIO
    # ======================================

    usuario = st.text_input(
        "Usuario"
    )

    password = st.text_input(
        "Contraseña",
        type="password"
    )

    ingresar = st.button(
        "INGRESAR"
    )

    # ======================================
    # LOGIN DEMO
    # ======================================

    if ingresar:

        if usuario == "admin" and password == "1234":

            st.success(
                "Bienvenido a SIGEM"
            )

        else:

            st.error(
                "Usuario o contraseña incorrectos"
            )
