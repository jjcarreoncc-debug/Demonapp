import streamlit as st


def sidebar_inventarios():

    with st.sidebar:

        st.markdown("""
        <style>

        section[data-testid="stSidebar"] {
            background-color: #f3f4f6;
        }

        div.stButton > button {
            width: 100%;
            border-radius: 12px;
            border: 1px solid #d1d5db;
            padding: 14px;
            text-align: left;
            font-size: 18px;
            background-color: white;
            margin-bottom: 10px;
        }

        div.stButton > button:hover {
            border: 1px solid #2563eb;
            background-color: #eff6ff;
        }

        </style>
        """, unsafe_allow_html=True)

        st.markdown("## 🏢 SIGEM")
        st.markdown("### 📦 Inventarios")

        st.markdown("---")

        if "subopcion_inv" not in st.session_state:
            st.session_state.subopcion_inv = "Productos"

        # =========================
        # MAESTROS
        # =========================
        st.markdown("### 🔹 Maestros")

        if st.button("📦 Productos", use_container_width=True):
            st.session_state.subopcion_inv = "Productos"

        if st.button("🏷️ Lotes / Series", use_container_width=True):
            st.session_state.subopcion_inv = "Lotes / Series"

        if st.button("📍 Ubicaciones", use_container_width=True):
            st.session_state.subopcion_inv = "Ubicaciones"

        # =========================
        # OPERACIONES
        # =========================
        st.markdown("### 🔄 Operaciones")

        if st.button("📥 Entradas", use_container_width=True):
            st.session_state.subopcion_inv = "Entradas"

        if st.button("📤 Salidas", use_container_width=True):
            st.session_state.subopcion_inv = "Salidas"

        if st.button("🔁 Transferencias", use_container_width=True):
            st.session_state.subopcion_inv = "Transferencias"

        # =========================
        # CONSULTAS
        # =========================
        st.markdown("### 📊 Consultas")

        if st.button("📋 Kardex", use_container_width=True):
            st.session_state.subopcion_inv = "Kardex"

        if st.button("🔍 Existencias", use_container_width=True):
            st.session_state.subopcion_inv = "Existencias"

        # =========================
        # INVENTARIO FISICO
        # =========================
        st.markdown("### 🧾 Inventario físico")

        if st.button("📌 Conteos cíclicos", use_container_width=True):
            st.session_state.subopcion_inv = "Conteos cíclicos"

        if st.button("✅ Ajustes", use_container_width=True):
            st.session_state.subopcion_inv = "Ajustes"

    return st.session_state.subopcion_inv
