import streamlit as st

def card_kpi(titulo, valor, color="#1f77b4"):

    st.markdown(f"""
    <div style="
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid {color};
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    ">
        <div style="font-size:18px; font-weight:600; color:#2c3e50;">
            {titulo}
        </div>
        <div style="font-size:30px; font-weight:700; color:{color}; margin-top:10px;">
            {valor}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# LOGOS
# =====================================

def mostrar_logos():

    col_logo_izq, col_logo_der = st.columns([1,1])

    with col_logo_izq:

        st.image(
            "LOOGO-TIDS-CONSULTING (2).jpg",
            width=180
        )

    with col_logo_der:

        st.markdown(
            """
            <div style="
                display:flex;
                justify-content:flex-end;
            ">
            """,
            unsafe_allow_html=True
        )

        st.image(
            "logo1.png",
            width=120
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )
