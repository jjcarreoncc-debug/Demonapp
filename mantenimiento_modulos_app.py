import streamlit as st
import pandas as pd

from mantenimiento_auditoria_app import registrar_auditoria
from database import get_connection


def administrar_modulos_app():

    st.subheader("🧱 Administrar módulos")

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================
    # CREAR TABLA MODULOS
    # =====================================
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS modulos (

            id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre_modulo TEXT UNIQUE,

            ruta TEXT,

            icono TEXT,

            orden_menu INTEGER,

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
            "➕ Crear módulo",
            "✏️ Modificar módulo",
            "🔎 Consultar módulos"
        ]
    )

    # =====================================
    # CREAR MODULO
    # =====================================
    with tab_crear:

        st.markdown("### ➕ Crear módulo")

        with st.form("crear_modulo_form"):

            nombre_modulo = st.text_input(
                "Nombre módulo"
            )

            ruta = st.text_input(
                "Ruta"
            )

            icono = st.text_input(
                "Icono",
                value="📊"
            )

            orden_menu = st.number_input(
                "Orden menú",
                min_value=1,
                value=1
            )

            activo = st.checkbox(
                "Activo",
                value=True
            )

            guardar = st.form_submit_button(
                "💾 Guardar módulo"
            )

            if guardar:

                if nombre_modulo.strip() == "":

                    st.warning(
                        "Ingrese nombre módulo"
                    )

                elif ruta.strip() == "":

                    st.warning(
                        "Ingrese ruta"
                    )

                else:

                    try:

                        cursor.execute(
                            """
                            INSERT INTO modulos (

                                nombre_modulo,
                                ruta,
                                icono,
                                orden_menu,
                                activo

                            )
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                nombre_modulo.strip(),
                                ruta.strip(),
                                icono.strip(),
                                orden_menu,
                                1 if activo else 0
                            )
                        )

                        conn.commit()

                        registrar_auditoria(
                            st.session_state.get("usuario", "SIN_USUARIO"),
                            "Módulos",
                            "CREAR",
                            f"Creó módulo {nombre_modulo.strip()}"
                        )

                        st.success(
                            "✅ Módulo creado correctamente"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Error al crear módulo: {e}"
                        )

    # =====================================
    # MODIFICAR MODULO
    # =====================================
    with tab_modificar:

        st.markdown("### ✏️ Modificar módulo")

        modulos_df = pd.read_sql_query(
            """
            SELECT
                id_modulo,
                nombre_modulo,
                ruta,
                icono,
                orden_menu,
                activo
            FROM modulos
            ORDER BY orden_menu
            """,
            conn
        )

        if modulos_df.empty:

            st.info(
                "No existen módulos para modificar"
            )

        else:

            opciones_modulos = {
                f"{row['icono']} {row['nombre_modulo']} - {row['ruta']}": row["id_modulo"]
                for _, row in modulos_df.iterrows()
            }

            modulo_seleccionado = st.selectbox(
                "Seleccione módulo",
                list(opciones_modulos.keys())
            )

            id_modulo = opciones_modulos[modulo_seleccionado]

            modulo_actual = modulos_df[
                modulos_df["id_modulo"] == id_modulo
            ].iloc[0]

            with st.form("modificar_modulo_form"):

                nuevo_nombre = st.text_input(
                    "Nombre módulo",
                    value=str(modulo_actual["nombre_modulo"])
                )

                nueva_ruta = st.text_input(
                    "Ruta",
                    value=str(modulo_actual["ruta"])
                )

                nuevo_icono = st.text_input(
                    "Icono",
                    value=str(modulo_actual["icono"])
                )

                nuevo_orden = st.number_input(
                    "Orden menú",
                    min_value=1,
                    value=int(modulo_actual["orden_menu"])
                )

                nuevo_activo = st.checkbox(
                    "Activo",
                    value=bool(modulo_actual["activo"])
                )

                guardar_cambios = st.form_submit_button(
                    "💾 Guardar cambios"
                )

                if guardar_cambios:

                    if nuevo_nombre.strip() == "":

                        st.warning(
                            "Ingrese nombre módulo"
                        )

                    elif nueva_ruta.strip() == "":

                        st.warning(
                            "Ingrese ruta"
                        )

                    else:

                        try:

                            cursor.execute(
                                """
                                UPDATE modulos
                                SET
                                    nombre_modulo = ?,
                                    ruta = ?,
                                    icono = ?,
                                    orden_menu = ?,
                                    activo = ?
                                WHERE id_modulo = ?
                                """,
                                (
                                    nuevo_nombre.strip(),
                                    nueva_ruta.strip(),
                                    nuevo_icono.strip(),
                                    nuevo_orden,
                                    1 if nuevo_activo else 0,
                                    id_modulo
                                )
                            )

                            conn.commit()

                            registrar_auditoria(
                                st.session_state.get("usuario", "SIN_USUARIO"),
                                "Módulos",
                                "ACTUALIZAR",
                                f"Actualizó módulo {nuevo_nombre.strip()}"
                            )

                            st.success(
                                "✅ Módulo actualizado correctamente"
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Error al actualizar módulo: {e}"
                            )

    # =====================================
    # CONSULTAR MODULOS
    # =====================================
    with tab_consultar:

        st.markdown("### 🔎 Consultar módulos")

        col1, col2 = st.columns(
            [3, 1]
        )

        with col1:

            filtro = st.text_input(
                "Buscar por nombre o ruta"
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
                id_modulo,
                icono,
                nombre_modulo,
                ruta,
                orden_menu,
                CASE
                    WHEN activo = 1 THEN 'Activo'
                    ELSE 'Inactivo'
                END AS estado
            FROM modulos
            WHERE 1 = 1
        """

        params = []

        if filtro.strip() != "":

            query += """
                AND (
                    nombre_modulo LIKE ?
                    OR ruta LIKE ?
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
            ORDER BY orden_menu
        """

        consulta_df = pd.read_sql_query(
            query,
            conn,
            params=params
        )

        if consulta_df.empty:

            st.info(
                "No se encontraron módulos"
            )

        else:

            st.dataframe(
                consulta_df,
                use_container_width=True,
                hide_index=True
            )

    conn.close()
