import streamlit as st

from mantenimiento_usuarios_app import alta_usuario_app
from mantenimiento_roles_app import asignar_roles_app
from mantenimiento_roles_app import crear_rol_app

def mantenimiento_app():

    st.title("🛠️ Mantenimiento")

    # =========================
    # VALIDACION
    # =========================
    if st.session_state.rol != "Admin":

        st.warning("⛔ No tienes permisos")
        st.stop()

    # =========================
    # SESSION STATE
    # =========================
    if "menu_mantenimiento" not in st.session_state:
        st.session_state.menu_mantenimiento = "👥 Usuarios"

    # =========================
    # MENU PRINCIPAL
    # =========================
    with st.sidebar:

        st.markdown("## 🛠️ Mantenimiento")

        menu = st.radio(
            "Módulo",
            [
                "👥 Usuarios",
                "🧩 Roles",
                "🔐 Permisos",
                "🧱 Módulos",
                "📜 Auditoría",
                "⚙️ Configuración"
            ],
            key="menu_mantenimiento"
        )

        if menu == "👥 Usuarios":

            submenu = st.radio(
                "Opciones",
                [
                    "Crear usuario",
                    "Editar usuario",
                    "Inactivar usuario",
                    "Consultar usuarios"
                ],
                key="submenu_usuarios"
            )

        elif menu == "🧩 Roles":

            submenu = st.radio(
                "Opciones",
                [
                    "Crear rol",
                    "Editar rol",
                    "Asignar usuarios"
                ],
                key="submenu_roles"
            )

        elif menu == "🔐 Permisos":

            submenu = st.radio(
                "Opciones",
                [
                    "Permisos por módulo",
                    "Permisos por rol",
                    "Acciones permitidas"
                ],
                key="submenu_permisos"
            )

        elif menu == "🧱 Módulos":

            submenu = st.radio(
                "Opciones",
                [
                    "Activar módulos",
                    "Ocultar módulos",
                    "Configuración visual"
                ],
                key="submenu_modulos"
            )

        elif menu == "📜 Auditoría":

            submenu = st.radio(
                "Opciones",
                [
                    "Inicios sesión",
                    "Cambios usuarios",
                    "Eliminaciones",
                    "Historial acciones"
                ],
                key="submenu_auditoria"
            )

        elif menu == "⚙️ Configuración":

            submenu = st.radio(
                "Opciones",
                [
                    "Variables sistema",
                    "Parámetros",
                    "Colores",
                    "Branding"
                ],
                key="submenu_configuracion"
            )

    # =========================
    # TITULO
    # =========================
    st.subheader(f"{menu} → {submenu}")
    st.write("DEBUG menu:", menu)
    st.write("DEBUG submenu:", submenu)
    # =========================
    # PANTALLAS
    # =========================
    if (
        menu == "👥 Usuarios"
        and submenu == "Crear usuario"
    ):

        alta_usuario_app()

    elif (
        menu == "🧩 Roles"
        and submenu == "Asignar usuarios"
    ):

        asignar_roles_app()

    else:

        st.info(
            f"Pantalla en construcción: {submenu}"
        )
