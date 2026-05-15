
import sqlite3
from sigem_db import get_db_path


def crear_tablas_seguridad():

    db_path = get_db_path("erp")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # =====================================================
    # TABLA USUARIOS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (

            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,

            usuario TEXT UNIQUE NOT NULL,

            nombre TEXT NOT NULL,

            email TEXT,

            telefono TEXT,

            password_hash TEXT,

            id_rol INTEGER,

            estado TEXT DEFAULT 'Activo',

            modulo_inicial TEXT DEFAULT 'Inicio',

            intentos_login INTEGER DEFAULT 0,

            bloqueado TEXT DEFAULT 'No',

            fecha_bloqueo TEXT,

            ultimo_login TEXT,

            usuario_creacion TEXT,

            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # =====================================================
    # TABLA ROLES
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS roles (

            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre_rol TEXT UNIQUE NOT NULL,

            descripcion TEXT,

            estado TEXT DEFAULT 'Activo',

            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # =====================================================
    # TABLA MODULOS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS modulos (

            id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre_modulo TEXT UNIQUE NOT NULL,

            descripcion TEXT,

            estado TEXT DEFAULT 'Activo',

            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # =====================================================
    # TABLA PERMISOS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS permisos (

            id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre_permiso TEXT UNIQUE NOT NULL,

            descripcion TEXT,

            estado TEXT DEFAULT 'Activo',

            fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # =====================================================
    # TABLA USUARIO ROLES
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario_roles (

            id_usuario_rol INTEGER PRIMARY KEY AUTOINCREMENT,

            id_usuario INTEGER,

            id_rol INTEGER,

            fecha_asignacion TEXT DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # =====================================================
    # TABLA ROL PERMISOS
    # =====================================================

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

    # =====================================================
    # TABLA SESIONES
    # =====================================================

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

    # =====================================================
    # VALIDAR COLUMNAS EXISTENTES
    # =====================================================

    cur.execute("""
        PRAGMA table_info(usuarios)
    """)

    columnas = [
        col[1]
        for col in cur.fetchall()
    ]

    # =====================================================
    # COLUMNAS NUEVAS
    # =====================================================

    nuevas_columnas = {

        "email":
            "TEXT",

        "telefono":
            "TEXT",

        "password_hash":
            "TEXT",

        "id_rol":
            "INTEGER",

        "estado":
            "TEXT DEFAULT 'Activo'",

        "modulo_inicial":
            "TEXT DEFAULT 'Inicio'",

        "intentos_login":
            "INTEGER DEFAULT 0",

        "bloqueado":
            "TEXT DEFAULT 'No'",

        "fecha_bloqueo":
            "TEXT",

        "ultimo_login":
            "TEXT",

        "usuario_creacion":
            "TEXT"

    }

    # =====================================================
    # ALTER TABLE AUTOMATICO
    # =====================================================

    for columna, tipo in nuevas_columnas.items():

        if columna not in columnas:

            sql = f"""
                ALTER TABLE usuarios
                ADD COLUMN {columna} {tipo}
            """

            cur.execute(sql)

            print(f"✅ Columna agregada: {columna}")

    # =====================================================
    # INSERTAR ROLES BASE
    # =====================================================

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
            SELECT id_rol
            FROM roles
            WHERE nombre_rol = ?
        """, (nombre_rol,))

        existe = cur.fetchone()

        if not existe:

            cur.execute("""
                INSERT INTO roles (
                    nombre_rol,
                    descripcion,
                    estado
                )
                VALUES (?, ?, 'Activo')
            """, (
                nombre_rol,
                descripcion
            ))

    # =====================================================
    # INSERTAR MODULOS BASE
    # =====================================================

    modulos_base = [

        ("Dashboard", "Dashboard principal"),
        ("Inventarios", "Modulo inventarios"),
        ("Compras", "Modulo compras"),
        ("Logistica", "Modulo logistica"),
        ("WMS", "Modulo almacen"),
        ("Mantenimiento", "Modulo mantenimiento")

    ]

    for nombre_modulo, descripcion in modulos_base:

        cur.execute("""
            SELECT id_modulo
            FROM modulos
            WHERE nombre_modulo = ?
        """, (nombre_modulo,))

        existe = cur.fetchone()

        if not existe:

            cur.execute("""
                INSERT INTO modulos (
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

    print("✅ Tablas de seguridad creadas/actualizadas correctamente.")
