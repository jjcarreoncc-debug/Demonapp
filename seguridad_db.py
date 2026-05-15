
import sqlite3
from sigem_db import get_db_path


def crear_tablas_seguridad():

    db_path = get_db_path("erp")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            nombre TEXT,
            correo TEXT,
            password TEXT,
            estatus TEXT DEFAULT 'Activo',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            estatus TEXT DEFAULT 'Activo',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS modulos (
            id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_modulo TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            estatus TEXT DEFAULT 'Activo',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS permisos (
            id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_permiso TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            estatus TEXT DEFAULT 'Activo',
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

    conn.commit()
    conn.close()
