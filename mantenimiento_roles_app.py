import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path

from ui_admin import (
    admin_css,
    admin_header
)


def get_conn_seguridad():

    db_path = get_db_path("seguridad")

    conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row

    return conn


def obtener_usuarios():

    conn = get_conn_seguridad()

    query = """
        SELECT
            id_usuario,
            usuario,
            nombre,
            id_rol,
            estado
        FROM usuarios
        ORDER BY usuario ASC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def obtener_roles():

    conn = get_conn_seguridad()

    query = """
        SELECT
            id_rol,
            nombre_rol,
            descripcion,
            estado
        FROM roles
        ORDER BY nombre_rol ASC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def asignar_roles_app():

    admin_css()

    admin_header(
        "🧩 Asignación de Roles",
        "Administración de roles y accesos del sistema."
    )

    st.divider()

    try:

        usuarios_df = obtener_usuarios()
        roles_df = obtener_roles()

    except Exception as e:

        st.error("❌ No se pudieron leer usuarios o roles.")
        st.exception(e)
        return

    if usuarios_df.empty:

        st.warning("⚠️ No hay usuarios registrados.")
        return

    if roles_df.empty:

        st.warning("⚠️ No hay roles registrados.")
        return

    st.markdown("### 👤 Usuario")

    usuario_sel = st.selectbox(
        "Selecciona usuario",
        usuarios_df["usuario"].tolist()
    )

    usuario_actual = usuarios_df[
        usuarios_df["usuario"] == usuario_sel
    ].iloc[0]

    st.markdown("### 🧩 Rol")

    roles_lista = roles_df["nombre_rol"].tolist()

    rol_actual_nombre = None

    if pd.notna(usuario_actual["id_rol"]):

        rol_match = roles_df[
            roles_df["id_rol"] == int(usuario_actual["id_rol"])
        ]

        if not rol_match.empty:

            rol_actual_nombre = rol_match.iloc[0]["nombre_rol"]

    if rol_actual_nombre in roles_lista:

        index_rol = roles_lista.index(rol_actual_nombre)

    else:

        index_rol = 0

    rol_sel = st.selectbox(
        "Selecciona rol",
        roles_lista,
        index=index_rol
    )

    rol_nuevo = roles_df[
        roles_df["nombre_rol"] == rol_sel
    ].iloc[0]

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

    if limpiar:

        st.rerun()

    if guardar:

        try:

            conn = get_conn_seguridad()

            cur = conn.cursor()

            cur.execute(
                """
                UPDATE usuarios
                SET id_rol = ?
                WHERE id_usuario = ?
                """,
                (
                    int(rol_nuevo["id_rol"]),
                    int(usuario_actual["id_usuario"])
                )
            )

            cur.execute(
                """
                INSERT INTO usuario_roles (
                    id_usuario,
                    id_rol
                )
                VALUES (?, ?)
                """,
                (
                    int(usuario_actual["id_usuario"]),
                    int(rol_nuevo["id_rol"])
                )
            )

            conn.commit()

            conn.close()

            st.success(
                f"✅ Rol '{rol_sel}' asignado correctamente a '{usuario_sel}'."
            )

            st.rerun()

        except Exception as e:

            st.error("❌ No se pudo asignar el rol.")
            st.exception(e)


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

    if limpiar:

        st.rerun()

    if guardar:

        if not nombre_rol.strip():

            st.warning(
                "⚠️ El nombre del rol es obligatorio."
            )

            return

        try:

            conn = get_conn_seguridad()

            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO roles (
                    nombre_rol,
                    descripcion,
                    estado
                )
                VALUES (?, ?, ?)
                """,
                (
                    nombre_rol.strip(),
                    descripcion.strip(),
                    estado
                )
            )

            conn.commit()

            conn.close()

            st.success(
                f"✅ Rol '{nombre_rol}' creado correctamente."
            )

            st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo guardar el rol. Puede que ya exista."
            )

            st.exception(e)
