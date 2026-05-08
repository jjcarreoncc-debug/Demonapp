import streamlit as st


# =========================
# CSS ADMIN
# =========================
def admin_css():

    st.markdown("""
    <style>

    .admin-card {
        background: white;
        padding: 28px;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        margin-bottom: 25px;
        border: 1px solid #ecf0f1;
    }

    .admin-title {
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 5px;
    }

    .admin-subtitle {
        color: #6b7280;
        margin-bottom: 25px;
        font-size: 14px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        margin-top: 10px;
        margin-bottom: 15px;
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
# CARD OPEN
# =========================
def admin_card_open():

    st.markdown(
        '<div class="admin-card">',
        unsafe_allow_html=True
    )


# =========================
# CARD CLOSE
# =========================
def admin_card_close():

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )
