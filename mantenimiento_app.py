import streamlit as st


def mantenimiento_app():

    st.title("🛠️ Mantenimiento")

    if st.session_state.rol != "Admin":
        st.warning("⛔ No tienes permisos")
        st.stop()

    if "mantenimiento_opcion" not in st.session_state:
        st.session_state.mantenimiento_opcion = "Consultas"

    st.sidebar.markdown("## 🛠️ Mantenimiento")

    opcion = st.sidebar.radio(
        "Submenú",
        [
            "Altas",
            "Bajas",
            "Consultas",
            "Modificaciones"
        ],
        key="mantenimiento_opcion"
    )

    st.subheader(f"📌 {opcion}")

    if opcion == "Altas":
        st.info("Aquí irán las altas de usuarios, roles, módulos y permisos.")

    elif opcion == "Bajas":
        st.info("Aquí irán las bajas de usuarios, roles y módulos.")

    elif opcion == "Consultas":
        st.info("Aquí irán las consultas de usuarios, roles, permisos y auditoría.")

    elif opcion == "Modificaciones":
        st.info("Aquí irán las modificaciones de usuarios, roles, permisos y estados.")
