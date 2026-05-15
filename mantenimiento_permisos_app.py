import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path

from ui_admin import (
    admin_css,
    admin_header
)


# =====================================
# CONEXION SEGURIDAD
# =====================================
def get_conn_seguridad():

    db_path = get_db_path("seguridad")

    conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row

    return conn


# =====================================
# VALIDAR TABLAS
# =====================================
def validar_tablas_permisos():

    conn = get_conn_seguridad()
    cursor = conn.cursor()

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
    conn.close()


# =====================================
# OBTENER ROLES
# =====================================
def obtener_roles():

    conn = get_conn_seguridad()

    df = pd.read_sql_query(
        """
        SELECT
            id_rol,
            nombre_rol,
            descripcion,
            estado
        FROM roles
        WHERE estado = 'Activo'
        ORDER BY nombre_rol
        """,
        conn
    )

    conn.close()

    return df


# =====================================
# OBTENER MODULOS ACTIVOS
# =====================================
def obtener_modulos_activos():

    conn = get_conn_seguridad()

    df = pd.read_sql_query(
        """
        SELECT
            id_modulo,
            nombre_modulo,
            ruta,
            icono,
            orden_menu,
            activo
        FROM modulos
        WHERE activo = 1
        ORDER BY orden_menu
        """,
        conn
    )

    conn.close()

    return df


# =====================================
# OBTENER PERMISOS POR ROL
# =====================================
def obtener_permisos_rol(id_rol):

    conn = get_conn_seguridad()

    df = pd.read_sql_query(
        """
        SELECT
            pr.id_permiso,
            pr.id_rol,
            pr.id_modulo,
            pr.puede_ver,
            pr.puede_crear,
            pr.puede_editar,
            pr.puede_eliminar,
            pr.puede_exportar,
            m.icono,
            m.nombre_modulo,
            m.ruta,
            m.orden_menu
        FROM permisos_roles pr
        INNER JOIN modulos m
            ON pr.id_modulo = m.id_modulo
        WHERE pr.id_rol = ?
        ORDER BY m.orden_menu
        """,
        conn,
        params=(id_rol,)
    )

    conn.close()

    return df


# =====================================
# APP PRINCIPAL PERMISOS
# =====================================
def permisos_por_modulo_app():

    validar_tablas_permisos()

    admin_css()

    admin_header(
        "🔐 Permisos por Módulo",
        "Asignación, modificación y consulta de accesos por rol."
    )

    st.divider()

    tab_asignar, tab_modificar, tab_consultar = st.tabs(
        [
            "➕ Asignar permisos",
            "✏️ Modificar permisos",
            "🔎 Consultar permisos"
        ]
    )

    # =====================================
    # ASIGNAR PERMISOS
    # =====================================
    with tab_asignar:

        st.markdown("### ➕ Asignar permisos")

        roles_df = obtener_roles()
        modulos_df = obtener_modulos_activos()

        if roles_df.empty:

            st.warning("⚠️ No existen roles activos.")
            return

        if modulos_df.empty:

            st.warning("⚠️ No existen módulos activos.")
            return

        rol_sel = st.selectbox(
            "Selecciona rol",
            roles_df["nombre_rol"].tolist(),
            key="asignar_permiso_rol"
        )

        rol_row = roles_df[
            roles_df["nombre_rol"] == rol_sel
        ].iloc[0]

        id_rol = int(rol_row["id_rol"])

        permisos_actuales_df = obtener_permisos_rol(id_rol)

        modulos_permitidos = permisos_actuales_df["id_modulo"].tolist()

        st.markdown("### 🧱 Módulos permitidos")

        permisos = {}

        c1, c2 = st.columns(2)

        for i, modulo in modulos_df.iterrows():

            id_modulo = int(modulo["id_modulo"])

            label_modulo = f"{modulo['icono']} {modulo['nombre_modulo']}"

            with c1 if i % 2 == 0 else c2:

                permisos[id_modulo] = st.checkbox(
                    label_modulo,
                    value=id_modulo in modulos_permitidos,
                    key=f"asignar_permiso_{id_rol}_{id_modulo}"
                )

        st.divider()

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:

            guardar = st.button(
                "💾 Guardar permisos",
                key="btn_guardar_permisos_asignar"
            )

        with col2:

            limpiar = st.button(
                "🔄 Limpiar",
                key="btn_limpiar_permisos_asignar"
            )

        if limpiar:

            st.rerun()

        if guardar:

            try:

                conn = get_conn_seguridad()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    DELETE FROM permisos_roles
                    WHERE id_rol = ?
                    """,
                    (
                        id_rol,
                    )
                )

                for id_modulo, permitido in permisos.items():

                    if permitido:

                        cursor.execute(
                            """
                            INSERT INTO permisos_roles (
                                id_rol,
                                id_modulo,
                                puede_ver,
                                puede_crear,
                                puede_editar,
                                puede_eliminar,
                                puede_exportar
                            )
                            VALUES (?, ?, 1, 0, 0, 0, 0)
                            """,
                            (
                                id_rol,
                                id_modulo
                            )
                        )

                conn.commit()
                conn.close()

                st.success(
                    f"✅ Permisos guardados correctamente para el rol '{rol_sel}'."
                )

                st.rerun()

            except Exception as e:

                st.error("❌ No se pudieron guardar los permisos.")
                st.exception(e)

    # =====================================
    # MODIFICAR PERMISOS
    # =====================================
    with tab_modificar:

        st.markdown("### ✏️ Modificar permisos")

        roles_df = obtener_roles()
        modulos_df = obtener_modulos_activos()

        if roles_df.empty:

            st.warning("⚠️ No existen roles activos.")
            return

        if modulos_df.empty:

            st.warning("⚠️ No existen módulos activos.")
            return

        rol_sel = st.selectbox(
            "Selecciona rol",
            roles_df["nombre_rol"].tolist(),
            key="modificar_permiso_rol"
        )

        rol_row = roles_df[
            roles_df["nombre_rol"] == rol_sel
        ].iloc[0]

        id_rol = int(rol_row["id_rol"])

        permisos_actuales_df = obtener_permisos_rol(id_rol)

        modulos_permitidos = permisos_actuales_df["id_modulo"].tolist()

        st.markdown("### 🧱 Accesos del rol")

        permisos = {}

        c1, c2 = st.columns(2)

        for i, modulo in modulos_df.iterrows():

            id_modulo = int(modulo["id_modulo"])

            label_modulo = f"{modulo['icono']} {modulo['nombre_modulo']}"

            with c1 if i % 2 == 0 else c2:

                permisos[id_modulo] = st.checkbox(
                    label_modulo,
                    value=id_modulo in modulos_permitidos,
                    key=f"modificar_permiso_{id_rol}_{id_modulo}"
                )

        st.divider()

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:

            guardar = st.button(
                "💾 Actualizar permisos",
                key="btn_actualizar_permisos"
            )

        with col2:

            limpiar = st.button(
                "🔄 Limpiar",
                key="btn_limpiar_permisos_modificar"
            )

        if limpiar:

            st.rerun()

        if guardar:

            try:

                conn = get_conn_seguridad()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    DELETE FROM permisos_roles
                    WHERE id_rol = ?
                    """,
                    (
                        id_rol,
                    )
                )

                for id_modulo, permitido in permisos.items():

                    if permitido:

                        cursor.execute(
                            """
                            INSERT INTO permisos_roles (
                                id_rol,
                                id_modulo,
                                puede_ver,
                                puede_crear,
                                puede_editar,
                                puede_eliminar,
                                puede_exportar
                            )
                            VALUES (?, ?, 1, 0, 0, 0, 0)
                            """,
                            (
                                id_rol,
                                id_modulo
                            )
                        )

                conn.commit()
                conn.close()

                st.success(
                    f"✅ Permisos actualizados correctamente para el rol '{rol_sel}'."
                )

                st.rerun()

            except Exception as e:

                st.error("❌ No se pudieron actualizar los permisos.")
                st.exception(e)

    # =====================================
    # CONSULTAR PERMISOS
    # =====================================
    with tab_consultar:

        st.markdown("### 🔎 Consultar permisos")

        roles_df = obtener_roles()

        if roles_df.empty:

            st.warning("⚠️ No existen roles activos.")
            return

        rol_sel = st.selectbox(
            "Selecciona rol",
            roles_df["nombre_rol"].tolist(),
            key="consultar_permiso_rol"
        )

        rol_row = roles_df[
            roles_df["nombre_rol"] == rol_sel
        ].iloc[0]

        id_rol = int(rol_row["id_rol"])

        permisos_df = obtener_permisos_rol(id_rol)

        if permisos_df.empty:

            st.info(
                f"El rol '{rol_sel}' no tiene módulos asignados."
            )

        else:

            consulta_df = permisos_df[
                [
                    "id_modulo",
                    "icono",
                    "nombre_modulo",
                    "ruta",
                    "puede_ver",
                    "puede_crear",
                    "puede_editar",
                    "puede_eliminar",
                    "puede_exportar"
                ]
            ].copy()

            consulta_df["puede_ver"] = consulta_df["puede_ver"].apply(
                lambda x: "Sí" if x == 1 else "No"
            )

            consulta_df["puede_crear"] = consulta_df["puede_crear"].apply(
                lambda x: "Sí" if x == 1 else "No"
            )

            consulta_df["puede_editar"] = consulta_df["puede_editar"].apply(
                lambda x: "Sí" if x == 1 else "No"
            )

            consulta_df["puede_eliminar"] = consulta_df["puede_eliminar"].apply(
                lambda x: "Sí" if x == 1 else "No"
            )

            consulta_df["puede_exportar"] = consulta_df["puede_exportar"].apply(
                lambda x: "Sí" if x == 1 else "No"
            )

            st.dataframe(
                consulta_df,
                use_container_width=True,
                hide_index=True
            )


# =====================================
# COMPATIBILIDAD MENÚ ANTERIOR
# =====================================
def permisos_por_rol_app():

    permisos_por_modulo_app()
