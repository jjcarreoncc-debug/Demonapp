import streamlit as st

from mantenimiento_auditoria_app import consultar_auditoria_app
from crear_tablas_app import crear_tablas_app
from revisar_estructura_db_app import revisar_estructura_db_app
from test_copiar_seguridad_desde_erp import copiar_seguridad_desde_erp_app

from mantenimiento_usuarios_app import (
    alta_usuario_app,
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

from carga_tablas_inicial_app import (
    carga_tablas_inicial_app
)



# =====================================================
# ESTILO SIDEBAR
# =====================================================

st.markdown(
    """
    <style>

    section[data-testid="stSidebar"] {
        background-color: #dbeafe;
    }

    div.stButton > button {

        background-color: #bfdbfe;

        border: 1px solid #93c5fd;

        color: #1e3a8a;

        border-radius: 10px;

        font-weight: 600;
    }

    div.stButton > button:hover {

        background-color: #93c5fd;

        color: #1e40af;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# BOTON MENU
# =====================================================



# =====================================================
# BOTON MENU
# =====================================================

def set_opcion_mantenimiento(
    menu,
    submenu,
    opcion
):

    st.session_state.menu_mantenimiento = menu
    st.session_state.submenu_mantenimiento = submenu
    st.session_state.opcion_mantenimiento = opcion


def boton_mantenimiento(
    texto,
    key,
    menu,
    submenu,
    opcion
):

    st.button(
        texto,
        use_container_width=True,
        key=key,
        on_click=set_opcion_mantenimiento,
        args=(menu, submenu, opcion)
    )


# =====================================================
# PANTALLA INICIO
# =====================================================

def inicio_mantenimiento_app():

    st.image(
        "logomantenimiento.jpg",
        use_container_width=True
    )

    st.success(
        """
        Bienvenido al módulo de mantenimiento SIGEM ERP.

        Desde este módulo podrás administrar:

        • Usuarios
        • Roles
        • Permisos
        • Auditoría
        • Configuración
        • Módulos del sistema
        """
    )


# =====================================================
# APP PRINCIPAL
# =====================================================

def mantenimiento_app():

    if "opcion_mantenimiento" not in st.session_state:

        st.session_state.opcion_mantenimiento = "🏠 Inicio"

    with st.sidebar:

        with st.expander(
            "🏠 Inicio",
            expanded=False
        ):

            boton_mantenimiento(
                "🏠 Inicio",
                "mnt_inicio",
                "Inicio",
                "Inicio",
                "🏠 Inicio"
            )

        with st.expander(
            "👥 Usuarios",
            expanded=False
        ):

            boton_mantenimiento(
                "➕ Crear usuario",
                "mnt_crear_usuario",
                "Usuarios",
                "Gestión usuarios",
                "➕ Crear usuario"
            )

            boton_mantenimiento(
                "✏️ Editar usuario",
                "mnt_editar_usuario",
                "Usuarios",
                "Gestión usuarios",
                "✏️ Editar usuario"
            )

            boton_mantenimiento(
                "📋 Consultar usuarios",
                "mnt_consultar_usuario",
                "Usuarios",
                "Gestión usuarios",
                "📋 Consultar usuarios"
            )

        with st.expander(
            "🧩 Roles",
            expanded=False
        ):

            boton_mantenimiento(
                "➕ Crear rol",
                "mnt_crear_rol",
                "Roles",
                "Gestión roles",
                "➕ Crear rol"
            )

            boton_mantenimiento(
                "👥 Asignar usuarios",
                "mnt_asignar_roles",
                "Roles",
                "Gestión roles",
                "👥 Asignar usuarios"
            )

        with st.expander(
            "🔐 Permisos",
            expanded=False
        ):

            boton_mantenimiento(
                "🔐 Permisos módulo",
                "mnt_perm_modulo",
                "Permisos",
                "Permisos",
                "🔐 Permisos módulo"
            )

            boton_mantenimiento(
                "🧩 Permisos rol",
                "mnt_perm_rol",
                "Permisos",
                "Permisos",
                "🧩 Permisos rol"
            )

        with st.expander(
            "🧱 Módulos",
            expanded=False
        ):

            boton_mantenimiento(
                "🧱 Administrar módulos",
                "mnt_modulos",
                "Módulos",
                "Módulos",
                "🧱 Administrar módulos"
            )

        with st.expander(
            "📜 Auditoría",
            expanded=False
        ):

            boton_mantenimiento(
                "📜 Historial acciones",
                "mnt_auditoria",
                "Auditoría",
                "Auditoría",
                "📜 Historial acciones"
            )

        with st.expander(
            "⚙️ Configuración",
            expanded=False
        ):

            boton_mantenimiento(
                "⚙️ Actualización tablas",
                "mnt_actualizacion",
                "Configuración",
                "Configuración",
                "⚙️ Actualización tablas"
            )

            boton_mantenimiento(
                "📦 Carga tablas inicial",
                "mnt_carga",
                "Configuración",
                "Configuración",
                "📦 Carga tablas inicial"
            )

            boton_mantenimiento(
                "🗄️ Crear tablas",
                "mnt_crear_tablas",
                "Configuración",
                "Configuración",
                "🗄️ Crear tablas"
            )

            boton_mantenimiento(
                "🔍 Revisar estructura DB",
                "mnt_estructura",
                "Configuración",
                "Configuración",
                "🔍 Revisar estructura DB"
            )

    opcion = st.session_state.opcion_mantenimiento

    if opcion == "🏠 Inicio":

        inicio_mantenimiento_app()

    elif opcion == "➕ Crear usuario":

        alta_usuario_app()

    elif opcion == "✏️ Editar usuario":

        editar_usuario_app()

    elif opcion == "📋 Consultar usuarios":

        consultar_usuarios_app()

    elif opcion == "➕ Crear rol":

        crear_rol_app()

    elif opcion == "👥 Asignar usuarios":

        asignar_roles_app()

    elif opcion == "🔐 Permisos módulo":

        permisos_por_modulo_app()

    elif opcion == "🧩 Permisos rol":

        permisos_por_rol_app()

    elif opcion == "🧱 Administrar módulos":

        administrar_modulos_app()

    elif opcion == "📜 Historial acciones":

        consultar_auditoria_app()

    elif opcion == "⚙️ Actualización tablas":

        actualizacion_tablas_app()

    elif opcion == "📦 Carga tablas inicial":

        carga_tablas_inicial_app()

    elif opcion == "🗄️ Crear tablas":

        crear_tablas_app()
	
    elif opcion == "🔍 Revisar estructura DB":

        revisar_estructura_db_app()

    else:

        st.info(
            f"Pantalla en construcción: {opcion}"
        )

# =====================================================
# EJECUTAR APP
# =====================================================

if __name__ == "__main__":

    mantenimiento_app()
