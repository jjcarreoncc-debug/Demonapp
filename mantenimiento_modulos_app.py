import streamlit as st
import pandas as pd
from mantenimiento_auditoria_app import registrar_auditoria

from database import get_connection


def administrar_modulos_app():

    st.subheader("🧱 Administrar módulos")

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================
    # CREAR TABLA
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

        guardar = st.form_submit_button(
            "💾 Guardar módulo"
        )

        if guardar:

            if nombre_modulo.strip() == "":

                st.warning(
                    "Ingrese nombre módulo"
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
                        VALUES (?, ?, ?, ?, 1)
                        """,
                        (
                            nombre_modulo.strip(),
                            ruta.strip(),
                            icono.strip(),
                            orden_menu
                        )
                    )

                    conn.commit()

                    st.success(
                        "✅ Módulo creado"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )

    st.divider()

    st.markdown("### 📋 Módulos registrados")

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
            "No existen módulos"
        )

    else:

        for _, row in modulos_df.iterrows():

            id_modulo = int(row["id_modulo"])

            col1, col2, col3, col4, col5 = st.columns(
                [3, 2, 1, 1, 1]
            )

            with col1:

                st.markdown(
                    f"""
                    {row['icono']} 
                    {row['nombre_modulo']}
                    """
                )

            with col2:

                st.caption(
                    row["ruta"]
                )

            with col3:

                activo = st.checkbox(
                    "Activo",
                    value=bool(row["activo"]),
                    key=f"activo_{id_modulo}"
                )

            with col4:

                nuevo_orden = st.number_input(
                    "Orden",
                    min_value=1,
                    value=int(row["orden_menu"]),
                    key=f"orden_{id_modulo}"
                )

            with col5:

                guardar_cambios = st.button(
                    "💾",
                    key=f"guardar_{id_modulo}"
                )

            if guardar_cambios:

                cursor.execute(
                    """
                    UPDATE modulos
                    SET
                        activo = ?,
                        orden_menu = ?
                    WHERE id_modulo = ?
                    """,
                    (
                        1 if activo else 0,
                        nuevo_orden,
                        id_modulo
                    )
                )

                conn.commit()
                registrar_auditoria(
                    st.session_state.usuario,
                    "Módulos",
                    "ACTUALIZAR",
                    f"Actualizó módulo {row['nombre_modulo']}"
                )
                st.success(
                    "✅ Módulo actualizado"
                )

                st.rerun()

    conn.close()
