import streamlit as st


def mantenimiento_app():

    st.title("🛠️ Mantenimiento")

    if st.session_state.rol != "Admin":
        st.warning("⛔ No tienes permisos")
        st.stop()

    if "mantenimiento_opcion" not in st.session_state:
        st.session_state.mantenimiento_opcion = "👥 Usuarios"

    with st.sidebar:

        st.markdown("## 🛠️ Mantenimiento")

        opcion = st.radio(
            "Submenú",
            [
                "👥 Usuarios",
                "🧩 Roles",
                "🔐 Permisos",
                "🧱 Módulos",
                "📜 Auditoría",
                "⚙️ Configuración"
            ],
            key="mantenimiento_opcion"
        )

    st.subheader(opcion)

    if opcion == "👥 Usuarios":
        st.info("Aquí irá la administración de usuarios.")

    elif opcion == "🧩 Roles":
        st.info("Aquí irá la administración de roles.")

    elif opcion == "🔐 Permisos":
        st.info("Aquí irá la administración de permisos.")

    elif opcion == "🧱 Módulos":
        st.info("Aquí irá la administración de módulos.")

    elif opcion == "📜 Auditoría":
        st.info("Aquí irá el historial y auditoría del sistema.")

    elif opcion == "⚙️ Configuración":
        st.info("Aquí irá la configuración general del sistema.")
