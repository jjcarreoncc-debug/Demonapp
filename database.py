
import sqlite3
from pathlib import Path


DB_PATH = Path("green_system.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT UNIQUE NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'Activo',
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            id_rol INTEGER,
            estado TEXT DEFAULT 'Activo',
            modulo_inicial TEXT,
            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
            ultimo_login TEXT,
            FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modulos (
            id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_modulo TEXT UNIQUE NOT NULL,
            ruta TEXT UNIQUE NOT NULL,
            icono TEXT,
            descripcion TEXT,
            visible INTEGER DEFAULT 1,
            estado TEXT DEFAULT 'Activo',
            orden_menu INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acciones (
            id_accion INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_accion TEXT UNIQUE NOT NULL,
            nombre_accion TEXT NOT NULL,
            descripcion TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permisos (
            id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
            id_rol INTEGER NOT NULL,
            id_modulo INTEGER NOT NULL,
            id_accion INTEGER NOT NULL,
            permitido INTEGER DEFAULT 1,
            FOREIGN KEY (id_rol) REFERENCES roles(id_rol),
            FOREIGN KEY (id_modulo) REFERENCES modulos(id_modulo),
            FOREIGN KEY (id_accion) REFERENCES acciones(id_accion)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            modulo TEXT,
            accion TEXT,
            detalle TEXT,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            ip TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            fecha_login TEXT DEFAULT CURRENT_TIMESTAMP,
            fecha_logout TEXT,
            estado TEXT DEFAULT 'Activa'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (
            id_config INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT UNIQUE NOT NULL,
            valor TEXT,
            tipo TEXT DEFAULT 'texto',
            descripcion TEXT,
            fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
