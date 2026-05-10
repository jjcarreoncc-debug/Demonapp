import streamlit as st


def sidebar_inventarios():

    with st.sidebar:

        st.markdown("## 🏢 SIGEM")
        st.markdown("### 📦 Inventarios")
        st.markdown("---")

        if "opcion_inv" not in st.session_state:
            st.session_state.opcion_inv = "Productos"

        if "subopcion_inv" not in st.session_state:
            st.session_state.subopcion_inv = "Maestro de productos"

        st.markdown("#### 📦 Productos")

        if st.button("📋 Maestro de productos", use_container_width=True):
            st.session_state.opcion_inv = "Productos"
            st.session_state.subopcion_inv = "Maestro de productos"

        if st.button("🏷️ Clasificaciones", use_container_width=True):
            st.session_state.opcion_inv = "Productos"
            st.session_state.subopcion_inv = "Clasificaciones"

        if st.button("📍 Ubicaciones", use_container_width=True):
            st.session_state.opcion_inv = "Productos"
            st.session_state.subopcion_inv = "Ubicaciones"

        if st.button("📦 Empaques", use_container_width=True):
            st.session_state.opcion_inv = "Productos"
            st.session_state.subopcion_inv = "Empaques"

        st.markdown("---")
        st.markdown("#### 🔄 Movimientos")

        if st.button("📥 Entradas", use_container_width=True):
            st.session_state.opcion_inv = "Movimientos"
            st.session_state.subopcion_inv = "Entradas"

        if st.button("📤 Salidas", use_container_width=True):
            st.session_state.opcion_inv = "Movimientos"
            st.session_state.subopcion_inv = "Salidas"

        if st.button("🔁 Transferencias", use_container_width=True):
            st.session_state.opcion_inv = "Movimientos"
            st.session_state.subopcion_inv = "Transferencias"

        st.markdown("---")
        st.markdown("#### 📊 Consultas")

        if st.button("📋 Kardex", use_container_width=True):
            st.session_state.opcion_inv = "Consultas"
            st.session_state.subopcion_inv = "Kardex"

        if st.button("🔍 Existencias", use_container_width=True):
            st.session_state.opcion_inv = "Consultas"
            st.session_state.subopcion_inv = "Existencias"

        st.markdown("---")
        st.markdown("#### 🧾 Inventario físico")

        if st.button("📌 Conteos cíclicos", use_container_width=True):
            st.session_state.opcion_inv = "Inventario físico"
            st.session_state.subopcion_inv = "Conteos cíclicos"

        if st.button("✅ Ajustes", use_container_width=True):
            st.session_state.opcion_inv = "Inventario físico"
            st.session_state.subopcion_inv = "Ajustes"

    return (
        st.session_state.opcion_inv,
        st.session_state.subopcion_inv
    )
