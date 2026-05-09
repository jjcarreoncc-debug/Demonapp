import sqlite3


# =========================================
# CONEXION
# ==========================================
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

            fecha_creacion DATETIME
            DEFAULT CURRENT_TIMESTAMP
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

            fecha_creacion DATETIME
            DEFAULT CURRENT_TIMESTAMP,

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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS auditoria (

            id_auditoria INTEGER PRIMARY KEY AUTOINCREMENT,

            usuario TEXT,

            modulo TEXT,

            accion TEXT,

            descripcion TEXT,

            fecha_hora DATETIME
            DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


# =========================================
# TABLA MODULOS
# =========================================
def crear_tabla_modulos():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS modulos (

            id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre_modulo TEXT UNIQUE,

            tipo TEXT,

            ruta TEXT,

            icono TEXT,

            orden_menu INTEGER,

            activo INTEGER DEFAULT 1
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

        (
            "Admin",
            "Administrador general"
        ),

        (
            "Gerencia",
            "Gerencia"
        ),

        (
            "Compras",
            "Modulo compras"
        ),

        (
            "Inventarios",
            "Modulo inventarios"
        ),

        (
            "Logistica",
            "Modulo logistica"
        ),

        (
            "WMS",
            "Modulo almacen"
        ),

        (
            "Consulta",
            "Solo consulta"
        )
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
# INSERTAR MODULOS BASE
# =========================================
def insertar_modulos_base():

    conn = get_connection()
    cursor = conn.cursor()

    modulos = [

        (
            "Dashboard",
            "dashboard",
            "dashboard_app",
            "📊",
            1
        ),

        (
            "Inventarios",
            "modulo",
            "inventarios_app",
            "📦",
            2
        ),

        (
            "Compras",
            "modulo",
            "compras_app",
            "🛒",
            3
        ),

        (
            "logistica",
            "modulo",
            "logistica_app",
            "🚚",
            4
        ),

        (
            "Almacen WMS",
            "modulo",
            "wms_app",
            "🏭",
            5
        ),

        (
            "Mantenimiento",
            "modulo",
            "mantenimiento_app",
            "🛠️",
            6
        )
    ]

    for modulo in modulos:

        try:

            cursor.execute(
                """
                INSERT INTO modulos (

                    nombre_modulo,
                    tipo,
                    ruta,
                    icono,
                    orden_menu

                )
                VALUES (?, ?, ?, ?, ?)
                """,
                modulo
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

crear_tabla_modulos()
# =========================================
# TABLA PERMISOS ROLES
# =========================================
def crear_tabla_permisos_roles():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS permisos_roles (

            id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,

            id_rol INTEGER,

            id_modulo INTEGER,

            puede_ver INTEGER DEFAULT 1,

            puede_crear INTEGER DEFAULT 0,

            puede_editar INTEGER DEFAULT 0,

            puede_eliminar INTEGER DEFAULT 0,

            puede_exportar INTEGER DEFAULT 0,

            FOREIGN KEY(id_rol)
            REFERENCES roles(id_rol),

            FOREIGN KEY(id_modulo)
            REFERENCES modulos(id_modulo)
        )
        """
    )

    conn.commit()
    conn.close()

insertar_roles_base()

insertar_modulos_base()
# =========================================
# INSERTAR PERMISOS BASE
# =========================================
def insertar_permisos_base():

    conn = get_connection()
    cursor = conn.cursor()

    permisos = [

        # =====================================
        # ADMIN
        # =====================================
        (1, 1, 1, 1, 1, 1, 1),
        (1, 2, 1, 1, 1, 1, 1),
        (1, 3, 1, 1, 1, 1, 1),
        (1, 4, 1, 1, 1, 1, 1),
        (1, 5, 1, 1, 1, 1, 1),
        (1, 6, 1, 1, 1, 1, 1),

        # =====================================
        # GERENCIA
        # =====================================
        (2, 1, 1, 0, 0, 0, 1),
        (2, 2, 1, 0, 0, 0, 1),
        (2, 3, 1, 0, 0, 0, 1),
        (2, 4, 1, 0, 0, 0, 1),

        # =====================================
        # COMPRAS
        # =====================================
        (3, 3, 1, 1, 1, 0, 1),

        # =====================================
        # INVENTARIOS
        # =====================================
        (4, 2, 1, 1, 1, 0, 1),

        # =====================================
        # LOGISTICA
        # =====================================
        (5, 4, 1, 1, 1, 0, 1),

        # =====================================
        # WMS
        # =====================================
        (6, 5, 1, 1, 1, 0, 1)
    ]

    for permiso in permisos:

        try:

            cursor.execute(
                """
                INSERT INTO permisos_roles (

                    id_rol,
                    id_modulo,

                    puede_ver,
                    puede_crear,
                    puede_editar,
                    puede_eliminar,
                    puede_exportar

                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                permiso
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

crear_tabla_modulos()

crear_tabla_permisos_roles()

insertar_roles_base()

insertar_modulos_base()

insertar_permisos_base()

print("✅ tablas creadas")
