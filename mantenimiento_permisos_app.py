
import streamlit as st
import pandas as pd

from database import get_connection

from ui_admin import (
    admin_css,
    admin_header
)


# =====================================
# PERMISOS POR ROL
# =====================================
def permisos_por_rol_app():

    st.markdown("## 🔐 Permisos por Rol")

    st.caption(
        "Administración dinámica de accesos por rol."
    )

    conn = get_connection()

    cursor = conn.cursor()

    # =====================================
    # CREAR TABLAS SI NO EXISTEN
    # =====================================
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS modulos (

            id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre_modulo TEXT UNIQUE,

            tipo TEXT,

            ruta TEXT,

            icono TEXT,

            orden_menu INTEGER,

            activo INTEGER DEFAULT 1
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS permisos_roles (

            id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,

            id_rol INTEGER,

            id_modulo INTEGER,

            puede_ver INTEGER DEFAULT 1,

            puede_crear INTEGER DEFAULT 0,

            puede_editar INTEGER DEFAULT 0,

            puede_eliminar INTEGER DEFAULT 0,

            puede_exportar INTEGER DEFAULT 0
        )
        """
    )

    conn.commit()

    # =====================================
    # ROLES
    # =====================================
    roles_df = pd.read_sql_query(
        """
        SELECT *
        FROM roles
        ORDER BY nombre_rol
        """,
        conn
    )

    # =====================================
    # MODULOS
    # =====================================
    modulos_df = pd.read_sql_query(
        """
        SELECT *
        FROM modulos
        WHERE activo = 1
        ORDER BY orden_menu
        """,
        conn
    )

    if roles_df.empty:

        st.warning("No existen roles.")

        conn.close()

        return

    if modulos_df.empty:

        st.warning("No existen módulos.")

        conn.close()

        return

    # =====================================
    # SELECCIONAR ROL
    # =====================================
    rol_sel = st.selectbox(
        "Rol",
        roles_df["nombre_rol"].tolist()
    )

    rol_row = roles_df[
        roles_df["nombre_rol"] == rol_sel
    ].iloc[0]

    id_rol = int(
        rol_row["id_rol"]
    )

    st.divider()

    st.markdown(
        "### 📋 Permisos módulos"
    )

    # =====================================
    # MODULOS
    # =====================================
    for _, modulo in modulos_df.iterrows():

        id_modulo = int(
            modulo["id_modulo"]
        )

        permiso_df = pd.read_sql_query(
            f"""
            SELECT *
            FROM permisos_roles
            WHERE id_rol = {id_rol}
            AND id_modulo = {id_modulo}
            """,
            conn
        )

        tiene_permiso = not permiso_df.empty

        col1, col2 = st.columns([4, 1])

        with col1:

            st.markdown(
                f"""
                ### {modulo['icono']} {modulo['nombre_modulo']}
                """
            )

        with col2:

            permiso = st.checkbox(
                "Acceso",
                value=tiene_permiso,
                key=f"{id_rol}_{id_modulo}"
            )

        # =====================================
        # INSERTAR
        # =====================================
        if permiso and not tiene_permiso:

            cursor.execute(
                """
                INSERT INTO permisos_roles (

                    id_rol,
                    id_modulo,
                    puede_ver

                )
                VALUES (?, ?, 1)
                """,
                (
                    id_rol,
                    id_modulo
                )
            )

            conn.commit()

            st.rerun()

        # =====================================
        # ELIMINAR
        # =====================================
        elif not permiso and tiene_permiso:

            cursor.execute(
                """
                DELETE FROM permisos_roles
                WHERE id_rol = ?
                AND id_modulo = ?
                """,
                (
                    id_rol,
                    id_modulo
                )
            )

            conn.commit()

            st.rerun()

    conn.close()


# =====================================
# PERMISOS POR MODULO
# =====================================
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

    st.markdown(
        "### 🧱 Módulos permitidos"
    )

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

        guardar = st.button(
            "💾 Guardar permisos"
        )

    with col2:

        limpiar = st.button(
            "🔄 Limpiar"
        )

    if limpiar:

        st.rerun()

    if guardar:

        modulos_permitidos = [

            modulo

            for modulo, permitido
            in permisos.items()

            if permitido
        ]

        st.success(
            f"✅ Permisos guardados para el rol '{rol}'."
        )

        st.json({

            "rol": rol,

            "modulos_permitidos": modulos_permitidos
        })
