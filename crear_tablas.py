import sqlite3


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

    # =====================================
    # BORRAR TABLA VIEJA
    # =====================================
    cursor.execute(
        "DROP TABLE IF EXISTS auditoria"
    )

    # =====================================
    # CREAR TABLA NUEVA
    # =====================================
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
# EJECUTAR
# =========================================
crear_tabla_roles()
crear_tabla_usuarios()
crear_tabla_auditoria()
insertar_roles_base()
