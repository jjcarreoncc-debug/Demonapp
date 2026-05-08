import streamlit as st

from ui_admin import (
    admin_css,
    admin_header
)


# =========================
# ASIGNAR ROLES
# =========================
def asignar_roles_app():

    admin_css()

    admin_header(
        "🧩 Asignación de Roles",
        "Administración de roles y accesos del sistema."
    )

    st.divider()

    # =========================
    # DATA DEMO
    # =========================
    usuarios = [
        "admin",
        "jose",
        "usuario_demo",
        "compras01",
        "wms01"
    ]

    roles = [
        "Admin",
        "Gerencia",
        "Compras",
        "Logistica",
        "WMS",
        "Consulta"
    ]

    # =========================
    # FORMULARIO
    # =========================
    st.markdown("### 👤 Usuario")

    usuario = st.selectbox(
        "Selecciona usuario",
        usuarios
    )

    st.markdown("### 🧩 Rol")

    rol = st.selectbox(
        "Selecciona rol",
        roles
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        guardar = st.button(
            "💾 Asignar rol"
        )

    with col2:
        limpiar = st.button(
            "🔄 Limpiar"
        )

    # =========================
    # LIMPIAR
    # =========================
    if limpiar:
        st.rerun()

    # =========================
    # GUARDAR
    # =========================
    if guardar:

        st.success(
            f"✅ Rol '{rol}' asignado correctamente a '{usuario}'."
        )

        st.json({
            "usuario": usuario,
            "rol_asignado": rol
        })


# =========================
# CREAR ROL
# =========================
def crear_rol_app():

    admin_css()

    admin_header(
        "🧩 Crear Rol",
        "Administración y creación de nuevos roles del sistema."
    )

    st.divider()

    st.markdown("### 📌 Información del rol")

    col1, col2 = st.columns(2)

    with col1:
        nombre_rol = st.text_input(
            "Nombre del rol *"
        )

    with col2:
        estado = st.selectbox(
            "Estado",
            [
                "Activo",
                "Inactivo"
            ]
        )

    descripcion = st.text_area(
        "Descripción del rol"
    )

    st.divider()

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])

    with col_btn1:
        guardar = st.button(
            "💾 Guardar rol"
        )

    with col_btn2:
        limpiar = st.button(
            "🔄 Limpiar"
        )

    # =========================
    # LIMPIAR
    # =========================
    if limpiar:
        st.rerun()

    # =========================
    # VALIDACIONES
    # =========================
    if guardar:

        if not nombre_rol:

            st.warning(
                "⚠️ El nombre del rol es obligatorio."
            )

        else:

            st.success(
                f"✅ Rol '{nombre_rol}' creado correctamente."
            )

            st.json({
                "rol": nombre_rol,
                "estado": estado,
                "descripcion": descripcion
            })
