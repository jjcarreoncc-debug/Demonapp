import sqlite3
import crear_tablas


# =========================================
# CONEXION
# =========================================
def get_connection():

    conn = sqlite3.connect(
        "erp.db",
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# =========================================
# TABLA ROLES
# =========================================
def crear_tabla_roles():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT UNIQUE,
            descripcion TEXT,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


# =========================================
# TABLA USUARIOS
# =========================================
def crear_tabla_usuarios():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            nombre TEXT,
            email TEXT,
            password_hash TEXT,
            id_rol INTEGER,
            estado TEXT,
            modulo_inicial TEXT,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultimo_login DATETIME,

            FOREIGN KEY(id_rol)
            REFERENCES roles(id_rol)
        )
        """
    )

    conn.commit()
    conn.close()


# =========================================
# TABLA AUDITORIA
# =========================================
def crear_tabla_auditoria():

    conn = get_connection()
    cursor = conn.cursor()

    # BORRAR SI EXISTE
    cursor.execute(
        "DROP TABLE IF EXISTS auditoria"
    )

    cursor.execute(
        """
        CREATE TABLE auditoria (
            id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            modulo TEXT,
            accion TEXT,
            descripcion TEXT,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


# =========================================
# INSERTAR ROLES BASE
# =========================================
def insertar_roles_base():

    conn = get_connection()
    cursor = conn.cursor()

    roles = [
        ("Admin", "Administrador general"),
        ("Gerencia", "Gerencia"),
        ("Compras", "Modulo compras"),
        ("Logistica", "Modulo logistica"),
        ("WMS", "Modulo almacen"),
        ("Consulta", "Solo consulta")
    ]

    for rol in roles:

        try:

            cursor.execute(
                """
                INSERT INTO roles (
                    nombre_rol,
                    descripcion
                )
                VALUES (?, ?)
                """,
                rol
            )

        except:

            pass

    conn.commit()
    conn.close()


# =========================================
# MAIN
# =========================================
def inicializar_bd():

    print("===================================")
    print("CREANDO TABLAS ERP")
    print("===================================")

    crear_tabla_roles()
    print("✅ Tabla roles creada")

    crear_tabla_usuarios()
    print("✅ Tabla usuarios creada")

    crear_tabla_auditoria()
    print("✅ Tabla auditoria creada")

    insertar_roles_base()
    print("✅ Roles base insertados")

    print("===================================")
    print("PROCESO FINALIZADO")
    print("===================================")
inicializar_bd()
