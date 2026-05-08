import streamlit as st


# =========================
# CSS ADMIN
# =========================
def admin_css():

    st.markdown("""
    <style>

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

    div.stButton > button {
        background-color: #1f77b4 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
        height: 45px !important;
    }

    div.stButton > button:hover {
        background-color: #155a86 !important;
        color: white !important;
    }

    div[data-testid="stTextInput"] input {
        border-radius: 10px;
    }

    div[data-testid="stSelectbox"] div {
        border-radius: 10px;
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
