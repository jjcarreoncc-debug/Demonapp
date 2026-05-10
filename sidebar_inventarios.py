import streamlit as st


def sidebar_inventarios():

    with st.sidebar:
        st.markdown("## 🏢 SIGEM")
        st.markdown("### 📦 Inventarios")
        st.markdown("---")

        if "opcion_inv" not in st.session_state:
            st.session_state.opcion_inv = "Productos"

        st.markdown("#### 📘 Maestros")
        if st.button("📦 Productos", use_container_width=True):
            st.session_state.opcion_inv = "Productos"
        if st.button("🏷️ Lotes / Series", use_container_width=True):
            st.session_state.opcion_inv = "Lotes / Series"
        if st.button("📍 Ubicaciones", use_container_width=True):
            st.session_state.opcion_inv = "Ubicaciones"

        st.markdown("#### 🔄 Operaciones")
        if st.button("📥 Entradas", use_container_width=True):
            st.session_state.opcion_inv = "Entradas"
        if st.button("📤 Salidas", use_container_width=True):
            st.session_state.opcion_inv = "Salidas"
        if st.button("🔁 Transferencias", use_container_width=True):
            st.session_state.opcion_inv = "Transferencias"

        st.markdown("#### 📊 Consultas")
        if st.button("📋 Kardex", use_container_width=True):
            st.session_state.opcion_inv = "Kardex"
        if st.button("🔍 Existencias", use_container_width=True):
            st.session_state.opcion_inv = "Existencias"

        st.markdown("#### 🧾 Inventario físico")
        if st.button("📌 Conteos cíclicos", use_container_width=True):
            st.session_state.opcion_inv = "Conteos cíclicos"
        if st.button("✅ Ajustes", use_container_width=True):
            st.session_state.opcion_inv = "Ajustes"

    return st.session_state.opcion_inv
