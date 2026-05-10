import sqlite3

# ==========================================
# CONEXIÓN
# ==========================================

conn = sqlite3.connect("sigem.db")

cursor = conn.cursor()

# ==========================================
# CREAR USUARIO ADMIN
# ==========================================

cursor.execute(
    """
    INSERT INTO usuarios (
        usuario,
        password,
        nombre_completo,
        rol,
        activo
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        "admin",
        "admin123",
        "Administrador General",
        "ALL",
        1
    )
)

conn.commit()

# ==========================================
# ASIGNAR TODOS LOS MÓDULOS
# ==========================================

cursor.execute(
    """
    SELECT id_modulo
    FROM modulos
    """
)

modulos = cursor.fetchall()

for modulo in modulos:

    id_modulo = modulo[0]

    cursor.execute(
        """
        INSERT INTO permisos_roles (
            id_rol,
            id_modulo,
            puede_ver
        )
        VALUES (?, ?, ?)
        """,
        (
            1,
            id_modulo,
            1
        )
    )

conn.commit()

conn.close()

print("ADMIN CREADO CORRECTAMENTE")
