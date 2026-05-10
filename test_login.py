import sqlite3
import hashlib

conn = sqlite3.connect("sigem.db")
cursor = conn.cursor()

password = "admin123"
password_hash = hashlib.sha256(password.encode()).hexdigest()

# Crear rol ALL si no existe
cursor.execute(
    """
    INSERT OR IGNORE INTO roles (
        nombre_rol,
        descripcion,
        estado
    )
    VALUES (?, ?, ?)
    """,
    (
        "ALL",
        "Perfil con acceso total",
        "Activo"
    )
)

conn.commit()

cursor.execute(
    """
    SELECT id_rol
    FROM roles
    WHERE nombre_rol = ?
    """,
    ("ALL",)
)

id_rol = cursor.fetchone()[0]

# Crear usuario admin
cursor.execute(
    """
    INSERT OR REPLACE INTO usuarios (
        id_usuario,
        usuario,
        nombre,
        email,
        password_hash,
        id_rol,
        estado,
        modulo_inicial
    )
    VALUES (
        COALESCE(
            (
                SELECT id_usuario
                FROM usuarios
                WHERE usuario = 'admin'
            ),
            NULL
        ),
        ?, ?, ?, ?, ?, ?, ?
    )
    """,
    (
        "admin",
        "Administrador General",
        "admin@sigem.com",
        password_hash,
        id_rol,
        "Activo",
        "dashboard_app"
    )
)

conn.commit()

# Dar acceso a todos los módulos activos al rol ALL
cursor.execute(
    """
    SELECT id_modulo
    FROM modulos
    WHERE activo = 1
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
        SELECT ?, ?, 1
        WHERE NOT EXISTS (
            SELECT 1
            FROM permisos_roles
            WHERE id_rol = ?
            AND id_modulo = ?
        )
        """,
        (
            id_rol,
            id_modulo,
            id_rol,
            id_modulo
        )
    )

conn.commit()
conn.close()

print("✅ Usuario admin creado/actualizado")
print("Usuario: admin")
print("Password: admin123")
