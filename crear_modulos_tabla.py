from database import get_connection


# =====================================
# CREAR TABLA MODULOS
# =====================================
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


# =====================================
# INSERTAR MODULOS BASE
# =====================================
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


# =====================================
# EJECUTAR
# =====================================
crear_tabla_modulos()

insertar_modulos_base()
