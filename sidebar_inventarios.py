import streamlit as st


def sidebar_inventarios():

    with st.sidebar:

        st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1f4e63, #2c6e8f);
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        div.stButton > button {
            width: 100%;
            text-align: left;
            border-radius: 12px;
            border: none;
            padding: 10px 14px;
            margin: 3px 0;
            background: rgba(255,255,255,0.12);
            color: white !important;
        }

        div.stButton > button:hover {
            background: rgba(255,255,255,0.25);
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("## 🏢 SIGEM")
        st.markdown("### 📦 Inventarios")
        st.divider()

        if "opcion_inv" not in st.session_state:
            st.session_state.opcion_inv = "Productos"

        with st.expander("📘 Maestros", expanded=True):
            if st.button("📦 Productos"):
                st.session_state.opcion_inv = "Productos"

            if st.button("🏷️ Lotes / Series"):
                st.session_state.opcion_inv = "Lotes / Series"

            if st.button("📍 Ubicaciones"):
                st.session_state.opcion_inv = "Ubicaciones"

        with st.expander("🔄 Operaciones", expanded=True):
            if st.button("📥 Entradas"):
                st.session_state.opcion_inv = "Entradas"

            if st.button("📤 Salidas"):
                st.session_state.opcion_inv = "Salidas"

            if st.button("🔁 Transferencias"):
                st.session_state.opcion_inv = "Transferencias"

        with st.expander("📊 Consultas"):
            if st.button("📋 Kardex"):
                st.session_state.opcion_inv = "Kardex"

            if st.button("🔍 Existencias"):
                st.session_state.opcion_inv = "Existencias"

        with st.expander("🧾 Inventario físico"):
            if st.button("📌 Conteos cíclicos"):
                st.session_state.opcion_inv = "Conteos cíclicos"

            if st.button("✅ Ajustes"):
                st.session_state.opcion_inv = "Ajustes"

        return st.session_state.opcion_inv
