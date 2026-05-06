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
