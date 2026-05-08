import streamlit as st


# =========================
# CSS ADMIN
# =========================
def admin_css():

    st.markdown("""
    <style>

    /* =========================
       TITULOS
    ========================= */

    .admin-title {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 5px;
    }

    .admin-subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    /* =========================
       BOTONES
    ========================= */

    div[data-testid="stButton"] > button {

        background-color: #1f77b4 !important;
        color: #ffffff !important;
        border: 1px solid #1f77b4 !important;

        border-radius: 10px !important;

        font-weight: 700 !important;

        height: 46px !important;

        opacity: 1 !important;

        box-shadow: 0 2px 8px rgba(0,0,0,0.08);

    }

    div[data-testid="stButton"] > button p {

        color: #ffffff !important;

        font-weight: 700 !important;

    }

    div[data-testid="stButton"] > button:hover {

        background-color: #155a86 !important;

        border-color: #155a86 !important;

        color: #ffffff !important;

    }

    /* =========================
       INPUTS
    ========================= */

    div[data-testid="stTextInput"] input {

        border-radius: 10px !important;

        border: 1px solid #d1d5db !important;

    }

    div[data-testid="stTextInput"] input:focus {

        border: 2px solid #1f77b4 !important;

        box-shadow: none !important;

    }

    /* =========================
       SELECTBOX
    ========================= */

    div[data-testid="stSelectbox"] div {

        border-radius: 10px !important;

    }

    /* =========================
       PASSWORD
    ========================= */

    div[data-testid="stTextInput"] {

        margin-bottom: 10px;

    }

    </style>
    """, unsafe_allow_html=True)


# =========================
# HEADER
# =========================
def admin_header(
    titulo,
    subtitulo
):

    st.markdown(
        f"""
        <div class="admin-title">
            {titulo}
        </div>

        <div class="admin-subtitle">
            {subtitulo}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# SECTION TITLE
# =========================
def admin_section(
    titulo
):

    st.markdown(
        f"""
        <div class="section-title">
            {titulo}
        </div>
        """,
        unsafe_allow_html=True
    )
