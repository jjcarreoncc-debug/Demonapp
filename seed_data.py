from database import get_connection


def seed_data():

    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # ROLES BASE
    # =========================
    roles = [
        ("Admin", "Administrador total"),
        ("Gerencia", "Gerencia general"),
        ("Compras", "Área de compras"),
        ("Logistica", "Área logística"),
        ("WMS", "Almacén y WMS"),
        ("Consulta", "Solo consultas")
    ]

    for rol in roles:

        cursor.execute("""
            INSERT OR IGNORE INTO roles (
                nombre_rol,
                descripcion
            )
            VALUES (?, ?)
        """, rol)

    # =========================
    # MODULOS
    # =========================
    modulos = [
        ("Inicio", "inicio", "🏠"),
        ("Dashboard", "dashboard", "📊"),
        ("Inventarios", "inventarios", "📦"),
        ("Compras", "compras", "🛒"),
        ("Logistica", "logistica", "🚚"),
        ("Almacen WMS", "wms", "🏭"),
        ("Mantenimiento", "mantenimiento", "🛠️")
    ]

    for modulo in modulos:

        cursor.execute("""
            INSERT OR IGNORE INTO modulos (
                nombre_modulo,
                ruta,
                icono
            )
            VALUES (?, ?, ?)
        """, modulo)

    # =========================
    # ACCIONES
    # =========================
    acciones = [
        ("VER", "Ver registros"),
        ("CREAR", "Crear registros"),
        ("EDITAR", "Editar registros"),
        ("ELIMINAR", "Eliminar registros"),
        ("EXPORTAR", "Exportar información"),
        ("ADMIN", "Administración total")
    ]

    for accion in acciones:

        cursor.execute("""
            INSERT OR IGNORE INTO acciones (
                codigo_accion,
                nombre_accion
            )
            VALUES (?, ?)
        """, accion)

    conn.commit()
    conn.close()

    print("✅ Seed data cargada.")
