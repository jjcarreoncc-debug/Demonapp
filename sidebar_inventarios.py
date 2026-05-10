#=========================
# MAESTROS
# =========================
st.markdown("### 🔹 Maestros")

with st.expander("📦 Productos", expanded=True):

    if st.button("📋 Maestro productos", use_container_width=True):
        st.session_state.subopcion_inv = "Maestro productos"

    if st.button("🏷️ Clasificaciones", use_container_width=True):
        st.session_state.subopcion_inv = "Clasificaciones"

    if st.button("📍 Ubicaciones", use_container_width=True):
        st.session_state.subopcion_inv = "Ubicaciones"

    if st.button("📦 Empaques", use_container_width=True):
        st.session_state.subopcion_inv = "Empaques"

with st.expander("🏷️ Lotes / Series"):

    if st.button("🔢 Series", use_container_width=True):
        st.session_state.subopcion_inv = "Series"

    if st.button("📦 Lotes", use_container_width=True):
        st.session_state.subopcion_inv = "Lotes"
