import streamlit as st
import sqlite3
import shutil
import os

from sigem_db import get_db_path


TABLAS_A_COPIAR = [
    "usuarios",
    "roles",
    "modulos",
    "permisos_roles",
    "auditoria"
]


def tabla_existe(conn, tabla):

    cur = conn.cursor()

    cur.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """,
        (tabla,)
    )

    return cur.fetchone() is not None


def copiar_tabla(origen_db, destino_db, tabla):

    conn_origen = sqlite3.connect(origen_db)
    conn_destino = sqlite3.connect(destino_db)

    cur_origen = conn_origen.cursor()
    cur_destino = conn_destino.cursor()

    if not tabla_existe(conn_origen, tabla):

        conn_origen.close()
        conn_destino.close()

        return False, f"⚠️ Tabla no encontrada: {tabla}"

    cur_origen.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """,
        (tabla,)
    )

    row = cur_origen.fetchone()

    if row is None:

        conn_origen.close()
        conn_destino.close()

        return False, f"⚠️ No se encontró CREATE TABLE de {tabla}"

    sql_create = row[0]

    cur_destino.execute(
        f"DROP TABLE IF EXISTS {tabla}"
    )

    cur_destino.execute(sql_create)

    cur_origen.execute(
        f"SELECT * FROM {tabla}"
    )

    filas = cur_origen.fetchall()

    columnas = [
        col[0]
        for col in cur_origen.description
    ]

    if filas:

        columnas_sql = ", ".join(columnas)

        placeholders = ", ".join(
            ["?"] * len(columnas)
        )

        cur_destino.executemany(
            f"""
            INSERT INTO {tabla} (
                {columnas_sql}
            )
            VALUES (
                {placeholders}
            )
            """,
            filas
        )

    conn_destino.commit()

    conn_origen.close()
    conn_destino.close()

    return True, f"✅ Tabla copiada: {tabla} | Registros: {len(filas)}"


def verificar_destino(destino_db):

    conn = sqlite3.connect(destino_db)

    cur = conn.cursor()

    cur.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
        """
    )

    tablas = [
        row[0]
        for row in cur.fetchall()
    ]

    resultado = {}

    for tabla in tablas:

        cur.execute(
            f"SELECT COUNT(*) FROM {tabla}"
        )

        resultado[tabla] = cur.fetchone()[0]

    conn.close()

    return resultado


def recuperar_seguridad():

    st.title("🔐 Recuperar Seguridad desde ERP")

    origen_db = get_db_path("erp")
    destino_db = get_db_path("seguridad")

    st.success(f"📥 ERP: {origen_db}")
    st.success(f"📤 SEGURIDAD: {destino_db}")

    st.subheader("📋 Tablas a copiar")

    st.write(TABLAS_A_COPIAR)

    confirmar = st.checkbox(
        "Confirmo reemplazar tablas en seguridad.db"
    )

    if st.button(
        "🚀 Ejecutar recuperación",
        use_container_width=True
    ):

        if not confirmar:

            st.warning(
                "⚠️ Debes confirmar antes de ejecutar."
            )

            return

        try:

            if os.path.exists(destino_db):

                backup_path = (
                    destino_db + ".backup"
                )

                shutil.copy2(
                    destino_db,
                    backup_path
                )

                st.success(
                    f"✅ Backup creado: {backup_path}"
                )

            for tabla in TABLAS_A_COPIAR:

                ok, mensaje = copiar_tabla(
                    origen_db,
                    destino_db,
                    tabla
                )

                if ok:
                    st.success(mensaje)
                else:
                    st.warning(mensaje)

            resumen = verificar_destino(
                destino_db
            )

            st.subheader(
                "✅ Resultado final"
            )

            st.json(resumen)

            st.success(
                "✅ Recuperación terminada correctamente."
            )

        except Exception as e:

            st.error(
                "❌ Error durante recuperación."
            )

            st.exception(e)


if __name__ == "__main__":

    recuperar_seguridad()
