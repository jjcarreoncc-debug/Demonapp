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


def validar_tabla_roles():

    conn = get_conn_seguridad()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT UNIQUE,
            descripcion TEXT,
            estado TEXT DEFAULT 'Activo'
        )
        """
    )

    cur.execute("PRAGMA table_info(roles)")
    columnas = [col[1] for col in cur.fetchall()]

    if "descripcion" not in columnas:
        cur.execute(
            """
            ALTER TABLE roles
            ADD COLUMN descripcion TEXT
            """
        )

    if "estado" not in columnas:
        cur.execute(
            """
            ALTER TABLE roles
            ADD COLUMN estado TEXT DEFAULT 'Activo'
            """
        )

    conn.commit()
    conn.close()


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

    validar_tabla_roles()

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

    validar_tabla_roles()

    admin_css()

    admin_header(
        "🧩 Mantenimiento de Roles",
        "Crear, modificar y consultar roles del sistema."
    )

    st.divider()

    tab_crear, tab_modificar, tab_consultar = st.tabs(
        [
            "➕ Crear rol",
            "✏️ Modificar rol",
            "🔎 Consultar roles"
        ]
    )

    # =====================================
    # CREAR ROL
    # =====================================
    with tab_crear:

        st.markdown("### 📌 Información del rol")

        col1, col2 = st.columns(2)

        with col1:

            nombre_rol = st.text_input(
                "Nombre del rol *",
                key="crear_nombre_rol"
            )

        with col2:

            estado = st.selectbox(
                "Estado",
                [
                    "Activo",
                    "Inactivo"
                ],
                key="crear_estado_rol"
            )

        descripcion = st.text_area(
            "Descripción del rol",
            key="crear_descripcion_rol"
        )

        st.divider()

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])

        with col_btn1:

            guardar = st.button(
                "💾 Guardar rol",
                key="btn_guardar_rol"
            )

        with col_btn2:

            limpiar = st.button(
                "🔄 Limpiar",
                key="btn_limpiar_rol"
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

    # =====================================
    # MODIFICAR ROL
    # =====================================
    with tab_modificar:

        st.markdown("### ✏️ Modificar rol")

        roles_df = obtener_roles()

        if roles_df.empty:

            st.warning("⚠️ No hay roles registrados.")

        else:

            roles_lista = roles_df["nombre_rol"].tolist()

            rol_sel = st.selectbox(
                "Selecciona rol a modificar",
                roles_lista,
                key="modificar_rol_sel"
            )

            rol_actual = roles_df[
                roles_df["nombre_rol"] == rol_sel
            ].iloc[0]

            st.markdown("### 📌 Datos del rol")

            col1, col2 = st.columns(2)

            with col1:

                nuevo_nombre = st.text_input(
                    "Nombre del rol *",
                    value=str(rol_actual["nombre_rol"]),
                    key="modificar_nombre_rol"
                )

            with col2:

                estado_actual = str(rol_actual["estado"])

                if estado_actual == "Inactivo":

                    index_estado = 1

                else:

                    index_estado = 0

                nuevo_estado = st.selectbox(
                    "Estado",
                    [
                        "Activo",
                        "Inactivo"
                    ],
                    index=index_estado,
                    key="modificar_estado_rol"
                )

            nueva_descripcion = st.text_area(
                "Descripción del rol",
                value=str(rol_actual["descripcion"])
                if rol_actual["descripcion"] is not None
                else "",
                key="modificar_descripcion_rol"
            )

            st.divider()

            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])

            with col_btn1:

                guardar_cambios = st.button(
                    "💾 Guardar cambios",
                    key="btn_guardar_cambios_rol"
                )

            with col_btn2:

                limpiar_modificar = st.button(
                    "🔄 Limpiar",
                    key="btn_limpiar_modificar_rol"
                )

            if limpiar_modificar:

                st.rerun()

            if guardar_cambios:

                if not nuevo_nombre.strip():

                    st.warning(
                        "⚠️ El nombre del rol es obligatorio."
                    )

                    return

                try:

                    conn = get_conn_seguridad()
                    cur = conn.cursor()

                    cur.execute(
                        """
                        UPDATE roles
                        SET
                            nombre_rol = ?,
                            descripcion = ?,
                            estado = ?
                        WHERE id_rol = ?
                        """,
                        (
                            nuevo_nombre.strip(),
                            nueva_descripcion.strip(),
                            nuevo_estado,
                            int(rol_actual["id_rol"])
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        f"✅ Rol '{nuevo_nombre}' actualizado correctamente."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "❌ No se pudo actualizar el rol."
                    )

                    st.exception(e)

    # =====================================
    # CONSULTAR ROLES
    # =====================================
    with tab_consultar:

        st.markdown("### 🔎 Consultar roles")

        roles_df = obtener_roles()

        if roles_df.empty:

            st.info("No hay roles registrados.")

        else:

            col1, col2 = st.columns([3, 1])

            with col1:

                filtro = st.text_input(
                    "Buscar por nombre o descripción",
                    key="consulta_filtro_roles"
                )

            with col2:

                filtro_estado = st.selectbox(
                    "Estado",
                    [
                        "Todos",
                        "Activo",
                        "Inactivo"
                    ],
                    key="consulta_estado_roles"
                )

            consulta_df = roles_df.copy()

            if filtro.strip():

                filtro_limpio = filtro.strip().lower()

                consulta_df = consulta_df[
                    consulta_df["nombre_rol"].astype(str).str.lower().str.contains(filtro_limpio)
                    |
                    consulta_df["descripcion"].astype(str).str.lower().str.contains(filtro_limpio)
                ]

            if filtro_estado != "Todos":

                consulta_df = consulta_df[
                    consulta_df["estado"] == filtro_estado
                ]

            st.markdown("### 📋 Roles registrados")

            st.dataframe(
                consulta_df,
                use_container_width=True,
                hide_index=True
            )


def modificar_rol_app():

    crear_rol_app()


def consultar_roles_app():

    crear_rol_app()
