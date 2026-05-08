
import streamlit as st

from ui_admin import (
    admin_css,
    admin_header
)


def permisos_por_modulo_app():

    admin_css()

    admin_header(
        "🔐 Permisos por Módulo",
        "Asignación de acceso a módulos por rol."
    )

    st.divider()

    roles = [
        "Admin",
        "Gerencia",
        "Compras",
        "Logistica",
        "WMS",
        "Consulta"
    ]

    modulos = [
        "Inicio",
        "Dashboard",
        "Inventarios",
        "Compras",
        "Logistica",
        "Almacen WMS",
        "Mantenimiento"
    ]

    rol = st.selectbox(
        "Selecciona rol",
        roles
    )

    st.markdown("### 🧱 Módulos permitidos")

    permisos = {}

    c1, c2 = st.columns(2)

    for i, modulo in enumerate(modulos):

        with c1 if i % 2 == 0 else c2:

            permisos[modulo] = st.checkbox(
                modulo,
                value=True if rol == "Admin" else False,
                key=f"permiso_{rol}_{modulo}"
            )

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        guardar = st.button("💾 Guardar permisos")

    with col2:
        limpiar = st.button("🔄 Limpiar")

    if limpiar:
        st.rerun()

    if guardar:

        modulos_permitidos = [
            modulo
            for modulo, permitido in permisos.items()
            if permitido
        ]

        st.success(
            f"✅ Permisos guardados para el rol '{rol}'."
        )

        st.json({
            "rol": rol,
            "modulos_permitidos": modulos_permitidos
        })
