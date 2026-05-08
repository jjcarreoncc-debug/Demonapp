import streamlit as st

from ui_admin import (
    admin_css,
    admin_header
)


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
