import streamlit as st


def compras_app():

    st.title("🛒 Compras")

    if "compras_vista" not in st.session_state:
        st.session_state.compras_vista = "menu"

    if st.session_state.compras_vista == "menu":

        c1, c2, c3 = st.columns(3)

        if c1.button("Dashboard"):
            st.session_state.compras_vista = "dashboard"
            st.rerun()

        if c2.button("Productos Comprados"):
            st.session_state.compras_vista = "productos"
            st.rerun()

        if c3.button("Proveedores"):
            st.session_state.compras_vista = "proveedores"
            st.rerun()

        c4, c5, c6 = st.columns(3)

        if c4.button("Bodegas"):
            st.session_state.compras_vista = "bodegas"
            st.rerun()

        if c5.button("Costos y Márgenes"):
            st.session_state.compras_vista = "costos"
            st.rerun()

        if c6.button("Detalle"):
            st.session_state.compras_vista = "detalle"
            st.rerun()

    if st.session_state.compras_vista != "menu":

        if st.button("🔙 Volver a Compras"):
            st.session_state.compras_vista = "menu"
            st.rerun()

    if st.session_state.compras_vista == "dashboard":
        st.subheader("📊 Dashboard Compras")
        st.info("Aquí irán los KPIs principales de compras.")

    elif st.session_state.compras_vista == "productos":
        st.subheader("📦 Productos Comprados")
        st.info("Aquí irán los indicadores por producto.")

    elif st.session_state.compras_vista == "proveedores":
        st.subheader("🏢 Proveedores")
        st.info("Aquí irán los indicadores por proveedor.")

    elif st.session_state.compras_vista == "bodegas":
        st.subheader("🏬 Bodegas")
        st.info("Aquí irán los indicadores por bodega.")

    elif st.session_state.compras_vista == "costos":
        st.subheader("💰 Costos y Márgenes")
        st.info("Aquí irán los costos, márgenes y rentabilidad.")

    elif st.session_state.compras_vista == "detalle":
        st.subheader("📋 Detalle Compras")
        st.info("Aquí irá la tabla completa de compras.")
