import streamlit as st

from mantenimiento_usuarios_app import (
    alta_usuario_app,
    consultar_usuarios_app,
    editar_usuario_app
)

from mantenimiento_roles_app import (
    asignar_roles_app,
    crear_rol_app
)

from mantenimiento_permisos_app import (
    permisos_por_modulo_app,
    permisos_por_rol_app
)

from mantenimiento_auditoria_app import (
    consultar_auditoria_app
)

from mantenimiento_modulos_app import (
    administrar_modulos_app
)


def mantenimiento_app():

    # =====================================================
    # SIDEBAR CORPORATIVO
    # =====================================================

    with st.sidebar:

        st.markdown("## 🛠️ Mantenimiento")
        st.caption("Administración del sistema")

        st.markdown("---")

        menu = st.radio(
            "Menú principal",
            [
                "🏠 Inicio",
                "👥 Usuarios",
                "🧩 Roles",
                "🔐 Permisos",
                "🧱 Módulos",
                "📜 Auditoría",
                "⚙️ Configuración"
            ],
            key="menu_mantenimiento"
        )

        st.markdown("---")

        submenu = None

        if menu == "👥 Usuarios":

            submenu = st.radio(
                "Usuarios",
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
                "Roles",
                [
                    "Crear rol",
                    "Editar rol",
                    "Asignar usuarios"
                ],
                key="submenu_roles"
            )

        elif menu == "🔐 Permisos":

            submenu = st.radio(
                "Permisos",
                [
                    "Permisos por módulo",
                    "Permisos por rol",
                    "Acciones permitidas"
                ],
                key="submenu_permisos"
            )

        elif menu == "🧱 Módulos":

            submenu = st.radio(
                "Módulos",
                [
                    "Administrar módulos"
                ],
                key="submenu_modulos"
            )

        elif menu == "📜 Auditoría":

            submenu = st.radio(
                "Auditoría",
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
                "Configuración",
                [
                    "Variables sistema",
                    "Parámetros",
                    "Colores",
                    "Branding"
                ],
                key="submenu_configuracion"
            )

        st.markdown("---")
        st.caption("SIGEM ERP")

    # =====================================================
    # HOME
    # =====================================================

    if menu == "🏠 Inicio":

        st.title("🛠️ Mantenimiento")

        st.info(
            "Seleccione una opción del menú lateral."
        )

        return

    # =====================================================
    # HEADER
    # =====================================================

    st.title("🛠️ Mantenimiento")

    st.caption(
        f"Mantenimiento / {menu} / {submenu}"
    )

    st.markdown("---")

    # =====================================================
    # USUARIOS
    # =====================================================

    if (
        menu == "👥 Usuarios"
        and submenu == "Crear usuario"
    ):

        alta_usuario_app()

    elif (
        menu == "👥 Usuarios"
        and submenu == "Editar usuario"
    ):

        editar_usuario_app()

    elif (
        menu == "👥 Usuarios"
        and submenu == "Consultar usuarios"
    ):

        consultar_usuarios_app()

    # =====================================================
    # ROLES
    # =====================================================

    elif (
        menu == "🧩 Roles"
        and submenu == "Crear rol"
    ):

        crear_rol_app()

    elif (
        menu == "🧩 Roles"
        and submenu == "Asignar usuarios"
    ):

        asignar_roles_app()

    # =====================================================
    # PERMISOS
    # =====================================================

    elif (
        menu == "🔐 Permisos"
        and submenu == "Permisos por módulo"
    ):

        permisos_por_modulo_app()

    elif (
        menu == "🔐 Permisos"
        and submenu == "Permisos por rol"
    ):

        permisos_por_rol_app()

    # =====================================================
    # MODULOS
    # =====================================================

    elif (
        menu == "🧱 Módulos"
        and submenu == "Administrar módulos"
    ):

        administrar_modulos_app()

    # =====================================================
    # AUDITORIA
    # =====================================================

    elif (
        menu == "📜 Auditoría"
        and submenu == "Historial acciones"
    ):

        consultar_auditoria_app()

    # =====================================================
    # DEFAULT
    # =====================================================

    else:

        st.info(
            f"Pantalla en construcción: {submenu}"
        )


if __name__ == "__main__":
    mantenimiento_app()
