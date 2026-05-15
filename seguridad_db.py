
import sqlite3
from sigem_db import get_db_path


def agregar_columna_si_no_existe(cur, tabla, columna, definicion):

    cur.execute(f"PRAGMA table_info({tabla})")
    columnas = [col[1] for col in cur.fetchall()]

    if columna not in columnas:
        cur.execute(f"""
            ALTER TABLE {tabla}
            ADD COLUMN {columna} {definicion}
        """)


def crear_tablas_seguridad():

    db_path = get_db_path("erp")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # =========================
    # CREAR TABLAS BASE
    # =========================

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

    # =========================
    # HOMOLOGAR USUARIOS
    # =========================

    agregar_columna_si_no_existe(cur, "usuarios", "email", "TEXT")
    agregar_columna_si_no_existe(cur, "usuarios", "telefono", "TEXT")
    agregar_columna_si_no_existe(cur, "usuarios", "password_hash", "TEXT")
    agregar_columna_si_no_existe(cur, "usuarios", "id_rol", "INTEGER")
    agregar_columna_si_no_existe(cur, "usuarios", "estado", "TEXT DEFAULT 'Activo'")
    agregar_columna_si_no_existe(cur, "usuarios", "modulo_inicial", "TEXT DEFAULT 'Inicio'")
    agregar_columna_si_no_existe(cur, "usuarios", "intentos_login", "INTEGER DEFAULT 0")
    agregar_columna_si_no_existe(cur, "usuarios", "bloqueado", "TEXT DEFAULT 'No'")
    agregar_columna_si_no_existe(cur, "usuarios", "fecha_bloqueo", "TEXT")
    agregar_columna_si_no_existe(cur, "usuarios", "ultimo_login", "TEXT")
    agregar_columna_si_no_existe(cur, "usuarios", "usuario_creacion", "TEXT")

    # =========================
    # HOMOLOGAR ROLES / MODULOS / PERMISOS
    # =========================

    agregar_columna_si_no_existe(cur, "roles", "estado", "TEXT DEFAULT 'Activo'")
    agregar_columna_si_no_existe(cur, "modulos", "estado", "TEXT DEFAULT 'Activo'")
    agregar_columna_si_no_existe(cur, "permisos", "estado", "TEXT DEFAULT 'Activo'")

    # =========================
    # COPIAR DATOS VIEJOS A NUEVOS
    # =========================

    cur.execute("""
        UPDATE usuarios
        SET email = correo
        WHERE email IS NULL
          AND correo IS NOT NULL
    """)

    cur.execute("""
        UPDATE usuarios
        SET password_hash = password
        WHERE password_hash IS NULL
          AND password IS NOT NULL
    """)

    cur.execute("""
        UPDATE usuarios
        SET estado = estatus
        WHERE estado IS NULL
          AND estatus IS NOT NULL
    """)

    cur.execute("""
        UPDATE roles
        SET estado = estatus
        WHERE estado IS NULL
          AND estatus IS NOT NULL
    """)

    cur.execute("""
        UPDATE modulos
        SET estado = estatus
        WHERE estado IS NULL
          AND estatus IS NOT NULL
    """)

    cur.execute("""
        UPDATE permisos
        SET estado = estatus
        WHERE estado IS NULL
          AND estatus IS NOT NULL
    """)

    # =========================
    # INSERTAR ROLES BASE
    # =========================

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

    # =========================
    # INSERTAR MODULOS BASE
    # =========================

    modulos_base = [
        ("Inicio", "Pantalla inicial"),
        ("Dashboard", "Dashboard principal"),
        ("Inventarios", "Modulo inventarios"),
        ("Compras", "Modulo compras"),
        ("Logistica", "Modulo logistica"),
        ("Almacen WMS", "Modulo almacen WMS"),
        ("Mantenimiento", "Modulo mantenimiento")
    ]

    for nombre_modulo, descripcion in modulos_base:

        cur.execute("""
            INSERT OR IGNORE INTO modulos (
                nombre_modulo,
                descripcion,
                estado
            )
            VALUES (?, ?, 'Activo')
        """, (
            nombre_modulo,
            descripcion
        ))

    conn.commit()
    conn.close()

    print("✅ Tablas de seguridad creadas y actualizadas correctamente.")
