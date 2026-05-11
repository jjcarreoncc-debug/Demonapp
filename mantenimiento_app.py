import streamlit as st
from mantenimiento_auditoria_app import consultar_auditoria_app

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

from mantenimiento_modulos_app import (
    administrar_modulos_app
)

from mantenimiento_actualizacion_tablas_app import (
    actualizacion_tablas_app
)

def mantenimiento_app():

    st.title("🛠️ Mantenimiento")

    if "menu_mantenimiento" not in st.session_state:
        st.session_state.menu_mantenimiento = "👥 Usuarios"

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

        # =========================
        # USUARIOS
        # =========================
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

        # =========================
        # ROLES
        # =========================
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

        # =========================
        # PERMISOS
        # =========================
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

        # =========================
        # MODULOS
        # =========================
        elif menu == "🧱 Módulos":

            submenu = st.radio(
                "Opciones",
                [
                    "Administrar módulos"
                ],
                key="submenu_modulos"
            )

        # =========================
        # AUDITORIA
        # =========================
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

        # =========================
        # CONFIGURACION
        # =========================
        elif menu == "⚙️ Configuración":

            submenu = st.radio(
                "Opciones",
                [
                    "Variables sistema",
                    "Parámetros",
                    "Colores",
                    "Branding",
                    "Actualización de tablas"
                ],
                key="submenu_configuracion"
            )

    st.caption(f"{menu} / {submenu}")

    # =========================
    # USUARIOS
    # =========================
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

    # =========================
    # ROLES
    # =========================
    elif (
        menu == "🧩 Roles"
        and submenu == "Asignar usuarios"
    ):

        asignar_roles_app()

    elif (
        menu == "🧩 Roles"
        and submenu == "Crear rol"
    ):

        crear_rol_app()

    # =========================
    # PERMISOS
    # =========================
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

    # =========================
    # MODULOS
    # =========================
    elif (
        menu == "🧱 Módulos"
        and submenu == "Administrar módulos"
    ):

        administrar_modulos_app()

    # =========================
    # AUDITORIA
    # =========================
    elif (
        menu == "📜 Auditoría"
        and submenu == "Historial acciones"
    ):

        consultar_auditoria_app()

    # =========================
    # CONFIGURACION
    # =========================
    elif (
        menu == "⚙️ Configuración"
        and submenu == "Actualización de tablas"
    ):

        st.subheader("🗄️ Actualización de tablas")
        actualizacion_tablas_app()

        st.info(
            "Aquí se configurarán las rutas y bases de datos por módulo."
        )

    # =========================
    # DEFAULT
    # =========================
    else:

        st.info(
            f"Pantalla en construcción: {submenu}"
        )
