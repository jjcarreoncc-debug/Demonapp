import sqlite3
import shutil
import os
import streamlit as st

from sigem_db import get_db_path


TABLAS_SEGURIDAD = [
    "usuarios",
    "roles",
    "modulos",
    "permisos",
    "usuario_roles",
    "rol_permisos",
    "sesiones_usuario"
]


def tabla_existe(conn, tabla):

    cur = conn.cursor()

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
    """, (tabla,))

    return cur.fetchone() is not None


def copiar_tabla(origen_db, destino_db, tabla):

    conn_origen = sqlite3.connect(origen_db)
    conn_destino = sqlite3.connect(destino_db)

    cur_origen = conn_origen.cursor()
    cur_destino = conn_destino.cursor()

    if not tabla_existe(conn_origen, tabla):

        conn_origen.close()
        conn_destino.close()

        return False, f"⚠️ La tabla {tabla} no existe en ERP. Se omitió."

    cur_origen.execute("""
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
    """, (tabla,))

    row = cur_origen.fetchone()

    sql_create = row[0]

    cur_destino.execute(f"DROP TABLE IF EXISTS {tabla}")

    cur_destino.execute(sql_create)

    cur_origen.execute(f"SELECT * FROM {tabla}")

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


def crear_tablas_faltantes(destino_db):

    conn = sqlite3.connect(destino_db)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            email TEXT,
            password_hash TEXT,
            id_rol INTEGER,
            estado TEXT DEFAULT 'Activo',
            modulo_inicial TEXT DEFAULT 'Inicio',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
            ultimo_login TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'Activo',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS modulos (
            id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_modulo TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'Activo',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS permisos (
            id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_permiso TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'Activo',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario_roles (
            id_usuario_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            id_rol INTEGER,
            fecha_asignacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS rol_permisos (
            id_rol_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
            id_rol INTEGER,
            id_permiso INTEGER,
            id_modulo INTEGER,
            puede_ver INTEGER DEFAULT 0,
            puede_crear INTEGER DEFAULT 0,
            puede_editar INTEGER DEFAULT 0,
            puede_borrar INTEGER DEFAULT 0,
            fecha_asignacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sesiones_usuario (
            id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            usuario TEXT,
            fecha_login TEXT DEFAULT CURRENT_TIMESTAMP,
            fecha_logout TEXT,
            estatus TEXT DEFAULT 'Activa'
        )
    """)

    roles_base = [
        ("Admin", "Administrador del sistema"),
        ("Gerencia", "Gerencia general"),
        ("Compras", "Modulo compras"),
        ("Logistica", "Modulo logistica"),
        ("WMS", "Modulo almacen WMS"),
        ("Consulta", "Solo consulta")
    ]

    for nombre_rol, descripcion in roles_base:

        cur.execute("""
            INSERT OR IGNORE INTO roles (
                nombre_rol,
                descripcion,
                estado
            )
            VALUES (?, ?, 'Activo')
        """, (
            nombre_rol,
            descripcion
        ))

    conn.commit()
    conn.close()


def verificar_destino(destino_db):

    conn = sqlite3.connect(destino_db)

    cur = conn.cursor()

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    tablas = [
        row[0]
        for row in cur.fetchall()
    ]

    resultado = {}

    for tabla in tablas:

        cur.execute(f"SELECT COUNT(*) FROM {tabla}")

        resultado[tabla] = cur.fetchone()[0]

    conn.close()

    return resultado


def copiar_seguridad_desde_erp_app():

    st.markdown("## 🧪 Copiar seguridad desde ERP")
    st.caption("Copia tablas de seguridad desde erp.db hacia seguridad.db.")

    origen_db = get_db_path("erp")
    destino_db = get_db_path("seguridad")

    st.info(f"📥 Origen ERP: {origen_db}")
    st.info(f"📤 Destino seguridad: {destino_db}")

    st.markdown("### Tablas de seguridad")
    st.write(TABLAS_SEGURIDAD)

    confirmar = st.checkbox(
        "Confirmo que quiero reemplazar las tablas existentes en seguridad.db"
    )

    if st.button("📋 Copiar tablas de seguridad"):

        if not confirmar:

            st.warning("⚠️ Debes confirmar antes de ejecutar.")
            return

        try:

            if os.path.exists(destino_db):

                backup_path = destino_db + ".backup"

                shutil.copy2(
                    destino_db,
                    backup_path
                )

                st.success(f"✅ Backup creado: {backup_path}")

            for tabla in TABLAS_SEGURIDAD:

                ok, mensaje = copiar_tabla(
                    origen_db,
                    destino_db,
                    tabla
                )

                if ok:
                    st.success(mensaje)
                else:
                    st.warning(mensaje)

            crear_tablas_faltantes(destino_db)

            st.success("✅ Tablas faltantes creadas si no existían.")

            resumen = verificar_destino(destino_db)

            st.markdown("### ✅ Resultado final en seguridad.db")

            st.json(resumen)

            st.success("✅ Proceso terminado correctamente.")

        except Exception as e:

            st.error("❌ Error copiando seguridad desde ERP.")
            st.exception(e)


if __name__ == "__main__":

    copiar_seguridad_desde_erp_app()
