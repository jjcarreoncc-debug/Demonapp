
import streamlit as st
import pandas as pd

from mantenimiento_auditoria_app import registrar_auditoria
from database import get_connection


def administrar_roles_app():

    st.subheader("👥 Administrar roles")

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================
    # CREAR TABLA ROLES
    # =====================================
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (

            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre_rol TEXT UNIQUE,

            descripcion TEXT,

            activo INTEGER DEFAULT 1
        )
        """
    )

    conn.commit()

    # =====================================
    # TABS
    # =====================================
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

        st.markdown("### ➕ Crear rol")

        with st.form("crear_rol_form"):

            nombre_rol = st.text_input(
                "Nombre rol"
            )

            descripcion = st.text_area(
                "Descripción"
            )

            activo = st.checkbox(
                "Activo",
                value=True
            )

            guardar = st.form_submit_button(
                "💾 Guardar rol"
            )

            if guardar:

                if nombre_rol.strip() == "":

                    st.warning(
                        "Ingrese nombre rol"
                    )

                else:

                    try:

                        cursor.execute(
                            """
                            INSERT INTO roles (

                                nombre_rol,
                                descripcion,
                                activo

                            )
                            VALUES (?, ?, ?)
                            """,
                            (
                                nombre_rol.strip(),
                                descripcion.strip(),
                                1 if activo else 0
                            )
                        )

                        conn.commit()

                        registrar_auditoria(
                            st.session_state.get("usuario", "SIN_USUARIO"),
                            "Roles",
                            "CREAR",
                            f"Creó rol {nombre_rol.strip()}"
                        )

                        st.success(
                            "✅ Rol creado correctamente"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Error al crear rol: {e}"
                        )

    # =====================================
    # MODIFICAR ROL
    # =====================================
    with tab_modificar:

        st.markdown("### ✏️ Modificar rol")

        roles_df = pd.read_sql_query(
            """
            SELECT
                id_rol,
                nombre_rol,
                descripcion,
                activo
            FROM roles
            ORDER BY nombre_rol
            """,
            conn
        )

        if roles_df.empty:

            st.info(
                "No existen roles para modificar"
            )

        else:

            opciones_roles = {
                f"{row['nombre_rol']}": row["id_rol"]
                for _, row in roles_df.iterrows()
            }

            rol_seleccionado = st.selectbox(
                "Seleccione rol",
                list(opciones_roles.keys())
            )

            id_rol = opciones_roles[rol_seleccionado]

            rol_actual = roles_df[
                roles_df["id_rol"] == id_rol
            ].iloc[0]

            with st.form("modificar_rol_form"):

                nuevo_nombre = st.text_input(
                    "Nombre rol",
                    value=str(rol_actual["nombre_rol"])
                )

                nueva_descripcion = st.text_area(
                    "Descripción",
                    value=str(rol_actual["descripcion"])
                    if rol_actual["descripcion"] is not None
                    else ""
                )

                nuevo_activo = st.checkbox(
                    "Activo",
                    value=bool(rol_actual["activo"])
                )

                guardar_cambios = st.form_submit_button(
                    "💾 Guardar cambios"
                )

                if guardar_cambios:

                    if nuevo_nombre.strip() == "":

                        st.warning(
                            "Ingrese nombre rol"
                        )

                    else:

                        try:

                            cursor.execute(
                                """
                                UPDATE roles
                                SET
                                    nombre_rol = ?,
                                    descripcion = ?,
                                    activo = ?
                                WHERE id_rol = ?
                                """,
                                (
                                    nuevo_nombre.strip(),
                                    nueva_descripcion.strip(),
                                    1 if nuevo_activo else 0,
                                    id_rol
                                )
                            )

                            conn.commit()

                            registrar_auditoria(
                                st.session_state.get("usuario", "SIN_USUARIO"),
                                "Roles",
                                "ACTUALIZAR",
                                f"Actualizó rol {nuevo_nombre.strip()}"
                            )

                            st.success(
                                "✅ Rol actualizado correctamente"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Error al actualizar rol: {e}"
                            )

    # =====================================
    # CONSULTAR ROLES
    # =====================================
    with tab_consultar:

        st.markdown("### 🔎 Consultar roles")

        col1, col2 = st.columns(
            [3, 1]
        )

        with col1:

            filtro = st.text_input(
                "Buscar por nombre o descripción"
            )

        with col2:

            filtro_activo = st.selectbox(
                "Estado",
                [
                    "Todos",
                    "Activos",
                    "Inactivos"
                ]
            )

        query = """
            SELECT
                id_rol,
                nombre_rol,
                descripcion,
                CASE
                    WHEN activo = 1 THEN 'Activo'
                    ELSE 'Inactivo'
                END AS estado
            FROM roles
            WHERE 1 = 1
        """

        params = []

        if filtro.strip() != "":

            query += """
                AND (
                    nombre_rol LIKE ?
                    OR descripcion LIKE ?
                )
            """

            params.extend(
                [
                    f"%{filtro.strip()}%",
                    f"%{filtro.strip()}%"
                ]
            )

        if filtro_activo == "Activos":

            query += " AND activo = 1 "

        elif filtro_activo == "Inactivos":

            query += " AND activo = 0 "

        query += """
            ORDER BY nombre_rol
        """

        consulta_df = pd.read_sql_query(
            query,
            conn,
            params=params
        )

        if consulta_df.empty:

            st.info(
                "No se encontraron roles"
            )

        else:

            st.dataframe(
                consulta_df,
                use_container_width=True,
                hide_index=True
            )

    conn.close()
