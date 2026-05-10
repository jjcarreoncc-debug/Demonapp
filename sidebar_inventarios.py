import streamlit as st


def sidebar_inventarios():

    with st.sidebar:

        st.markdown("## 🏢 SIGEM")
        st.markdown("---")

        if "subopcion_inv" not in st.session_state:
            st.session_state.subopcion_inv = "Productos"

        # =========================
        # PRODUCTOS
        # =========================
        with st.expander("📦 Inventarios", expanded=True):

            if st.button("Productos"):
                st.session_state.subopcion_inv = "Productos"

            if st.button("Lotes / Series"):
                st.session_state.subopcion_inv = "Lotes / Series"

            if st.button("Ubicaciones"):
                st.session_state.subopcion_inv = "Ubicaciones"

        # =========================
        # OPERACIONES
        # =========================
        with st.expander("🔄 Operaciones", expanded=False):

            if st.button("Entradas"):
                st.session_state.subopcion_inv = "Entradas"

            if st.button("Salidas"):
                st.session_state.subopcion_inv = "Salidas"

            if st.button("Transferencias"):
                st.session_state.subopcion_inv = "Transferencias"

        # =========================
        # CONSULTAS
        # =========================
        with st.expander("📊 Consultas", expanded=False):

            if st.button("Kardex"):
                st.session_state.subopcion_inv = "Kardex"

            if st.button("Existencias"):
                st.session_state.subopcion_inv = "Existencias"

    return st.session_state.subopcion_inv
