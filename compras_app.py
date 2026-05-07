# =========================
# MENÚ COMPRAS
# =========================
def aplicar_css_compras():
    st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 70px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        background-color: #1f77b4;
        color: white;
    }

    div.stButton > button:hover {
        background-color: #145a86;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
if st.session_state.compras_vista == "menu":

    # FILA 1
    c1, c2, c3 = st.columns(3)
    
    if c1.button("📊 Dashboard"):
        st.session_state.compras_vista = "dashboard"
        st.rerun()

    if c2.button("📦 Productos"):
        st.session_state.compras_vista = "productos"
        st.rerun()

    if c3.button("🏢 Proveedores"):
        st.session_state.compras_vista = "proveedores"
        st.rerun()

    # FILA 2
    c4, c5, c6 = st.columns([1,1,1])

    if c4.button("🏬 Bodegas"):
        st.session_state.compras_vista = "bodegas"
        st.rerun()

    if c5.button("💰 Costos"):
        st.session_state.compras_vista = "costos"
        st.rerun()

    # ESPACIO VACÍO EN c6
