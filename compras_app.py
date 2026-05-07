# =========================
# MENÚ COMPRAS
# =========================
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
