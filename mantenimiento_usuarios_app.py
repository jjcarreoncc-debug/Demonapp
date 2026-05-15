import streamlit as st
import pandas as pd
import sqlite3

from sigem_db import get_db_path

import mantenimiento_auditoria_app as auditoria


# =====================================================
# ALTA USUARIO
# =====================================================

def alta_usuario_app():

    db_path = get_db_path("seguridad")

    conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    st.markdown("### 📌 Información básica")

    col1, col2, col3 = st.columns(3)

    with col1:
        usuario = st.text_input("Usuario *")

    with col2:
        nombre = st.text_input("Nombre completo *")

    with col3:
        email = st.text_input("Correo electrónico *")

    st.markdown("### 🔐 Seguridad")

    col4, col5, col6 = st.columns(3)

    with col4:
        password = st.text_input(
            "Password temporal *",
            type="password"
        )

    with col5:
        confirmar_password = st.text_input(
            "Confirmar password *",
            type="password"
        )

    with col6:
        estado = st.selectbox(
            "Estado",
            ["Activo", "Inactivo"]
        )

    st.markdown("### 🧩 Acceso")

    col7, col8 = st.columns(2)

    roles_df = pd.read_sql_query(
        """
        SELECT nombre_rol
        FROM roles
        WHERE estado = 'Activo'
        ORDER BY nombre_rol
        """,
        conn
    )

    lista_roles = roles_df["nombre_rol"].tolist()

    modulos_df = pd.read_sql_query(
        """
        SELECT nombre_modulo
        FROM modulos
        WHERE activo = 1
        ORDER BY orden_menu
        """,
        conn
    )

    lista_modulos = modulos_df["nombre_modulo"].tolist()

    with col7:
        rol = st.selectbox(
            "Rol *",
            lista_roles
        )

    with col8:
        modulo_inicial = st.selectbox(
            "Módulo inicial",
            lista_modulos
        )

    st.divider()

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])

    with col_btn1:
        guardar = st.button("💾 Guardar usuario")

    with col_btn2:
        limpiar = st.button("🔄 Limpiar")

    if limpiar:

        conn.close()

        st.rerun()

    if guardar:

        if (
            not usuario
            or not nombre
            or not email
            or not password
            or not confirmar_password
        ):

            st.warning(
                "⚠️ Completa todos los campos obligatorios."
            )

        elif password != confirmar_password:

            st.error(
                "❌ Las contraseñas no coinciden."
            )

        else:

            rol_row = cursor.execute(
                """
                SELECT id_rol
                FROM roles
                WHERE nombre_rol = ?
                """,
                (rol,)
            ).fetchone()

            if rol_row is None:

                st.error(
                    "❌ El rol seleccionado no existe en la base de datos."
                )

                conn.close()

                return

            try:

                cursor.execute(
                    """
                    INSERT INTO usuarios (
                        usuario,
                        nombre,
                        email,
                        password_hash,
                        id_rol,
                        estado,
                        modulo_inicial
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        usuario,
                        nombre,
                        email,
                        password,
                        rol_row["id_rol"],
                        estado,
                        modulo_inicial
                    )
                )

                conn.commit()

                st.success(
                    "✅ Usuario guardado correctamente."
                )

                auditoria.registrar_auditoria(
                    usuario=usuario,
                    modulo="Usuarios",
                    accion="Crear usuario",
                    descripcion=f"Se creó el usuario {usuario}"
                )

            except Exception as e:

                st.error(
                    "❌ No se pudo guardar el usuario."
                )

                st.exception(e)

            finally:

                conn.close()


# =====================================================
# EDITAR USUARIO
# =====================================================

def editar_usuario_app():

    st.markdown("## ✏️ Editar usuario")

    st.caption(
        "Modifica datos básicos, rol, estado y módulo inicial del usuario."
    )

    try:

        db_path = get_db_path("seguridad")

        conn = sqlite3.connect(db_path)

        conn.row_factory = sqlite3.Row

        query = """
            SELECT
                u.id_usuario,
                u.usuario,
                u.nombre,
                u.email,
                r.nombre_rol AS rol,
                u.id_rol,
                u.estado,
                u.modulo_inicial
            FROM usuarios u
            LEFT JOIN roles r
                ON u.id_rol = r.id_rol
            ORDER BY u.usuario ASC
        """

        df = pd.read_sql_query(query, conn)

        roles_df = pd.read_sql_query(
            """
            SELECT
                id_rol,
                nombre_rol
            FROM roles
            WHERE estado = 'Activo'
            ORDER BY nombre_rol ASC
            """,
            conn
        )

        modulos_df = pd.read_sql_query(
            """
            SELECT nombre_modulo
            FROM modulos
            WHERE activo = 1
            ORDER BY orden_menu
            """,
            conn
        )

        conn.close()

    except Exception as e:

        st.error(
            "❌ No se pudo conectar o leer la base de datos."
        )

        st.exception(e)

        return

    if df.empty:

        st.info(
            "No hay usuarios registrados para editar."
        )

        return

    if roles_df.empty:

        st.warning(
            "No hay roles registrados. Primero crea roles."
        )

        return

    usuario_sel = st.selectbox(
        "Selecciona el usuario a editar",
        df["usuario"].tolist()
    )

    usuario_actual = df[
        df["usuario"] == usuario_sel
    ].iloc[0]

    st.divider()

    st.markdown("### 📌 Información básica")

    col1, col2, col3 = st.columns(3)

    with col1:

        nuevo_usuario = st.text_input(
            "Usuario *",
            value=str(usuario_actual["usuario"])
        )

    with col2:

        nuevo_nombre = st.text_input(
            "Nombre completo *",
            value=str(usuario_actual["nombre"])
        )

    with col3:

        nuevo_email = st.text_input(
            "Correo electrónico *",
            value=str(usuario_actual["email"])
        )

    st.markdown("### 🧩 Acceso")

    lista_roles = roles_df["nombre_rol"].tolist()

    rol_actual = (
        usuario_actual["rol"]
        if usuario_actual["rol"] in lista_roles
        else lista_roles[0]
    )

    index_rol = lista_roles.index(rol_actual)

    col4, col5, col6 = st.columns(3)

    with col4:

        nuevo_rol = st.selectbox(
            "Rol *",
            lista_roles,
            index=index_rol
        )

    with col5:

        nuevo_estado = st.selectbox(
            "Estado",
            ["Activo", "Inactivo"],
            index=0 if usuario_actual["estado"] == "Activo" else 1
        )

    with col6:

        modulos = modulos_df["nombre_modulo"].tolist()

        modulo_actual = (
            usuario_actual["modulo_inicial"]
            if usuario_actual["modulo_inicial"] in modulos
            else modulos[0]
        )

        nuevo_modulo = st.selectbox(
            "Módulo inicial",
            modulos,
            index=modulos.index(modulo_actual)
        )

    st.markdown("### 🔐 Seguridad")

    cambiar_password = st.checkbox(
        "Cambiar password"
    )

    nuevo_password = ""

    confirmar_password = ""

    if cambiar_password:

        col7, col8 = st.columns(2)

        with col7:

            nuevo_password = st.text_input(
                "Nuevo password",
                type="password"
            )

        with col8:

            confirmar_password = st.text_input(
                "Confirmar nuevo password",
                type="password"
            )

    st.divider()

    guardar = st.button(
        "💾 Guardar cambios"
    )

    if guardar:

        if (
            not nuevo_usuario
            or not nuevo_nombre
            or not nuevo_email
        ):

            st.warning(
                "⚠️ Completa todos los campos obligatorios."
            )

            return

        if cambiar_password and not nuevo_password:

            st.warning(
                "⚠️ Debes escribir el nuevo password."
            )

            return

        if cambiar_password and nuevo_password != confirmar_password:

            st.error(
                "❌ Las contraseñas no coinciden."
            )

            return

        try:

            db_path = get_db_path("seguridad")

            conn = sqlite3.connect(db_path)

            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()

            rol_row = cursor.execute(
                """
                SELECT id_rol
                FROM roles
                WHERE nombre_rol = ?
                """,
                (nuevo_rol,)
            ).fetchone()

            if rol_row is None:

                st.error(
                    "❌ El rol seleccionado no existe."
                )

                conn.close()

                return

            if cambiar_password:

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET
                        usuario = ?,
                        nombre = ?,
                        email = ?,
                        password_hash = ?,
                        id_rol = ?,
                        estado = ?,
                        modulo_inicial = ?
                    WHERE id_usuario = ?
                    """,
                    (
                        nuevo_usuario,
                        nuevo_nombre,
                        nuevo_email,
                        nuevo_password,
                        rol_row["id_rol"],
                        nuevo_estado,
                        nuevo_modulo,
                        int(usuario_actual["id_usuario"])
                    )
                )

            else:

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET
                        usuario = ?,
                        nombre = ?,
                        email = ?,
                        id_rol = ?,
                        estado = ?,
                        modulo_inicial = ?
                    WHERE id_usuario = ?
                    """,
                    (
                        nuevo_usuario,
                        nuevo_nombre,
                        nuevo_email,
                        rol_row["id_rol"],
                        nuevo_estado,
                        nuevo_modulo,
                        int(usuario_actual["id_usuario"])
                    )
                )

            conn.commit()

            conn.close()

            st.success(
                "✅ Usuario actualizado correctamente."
            )

            st.rerun()

        except Exception as e:

            st.error(
                "❌ No se pudo actualizar el usuario."
            )

            st.exception(e)
