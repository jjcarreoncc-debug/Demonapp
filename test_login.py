import hashlib
from database import get_connection

conn = get_connection()
cursor = conn.cursor()

password = "admin123"
password_hash = hashlib.sha256(password.encode()).hexdigest()

cursor.execute(
    """
    INSERT OR IGNORE INTO roles (
        nombre_rol,
        descripcion
    )
    VALUES (?, ?)
    """,
    (
        "ALL",
        "Acceso total sistema"
    )
)

conn.commit()

id_rol = cursor.execute(
    """
    SELECT id_rol
    FROM roles
    WHERE nombre_rol = ?
    """,
    ("ALL",)
).fetchone()[0]

usuario_existente = cursor.execute(
    """
    SELECT id_usuario
    FROM usuarios
    WHERE usuario = ?
    """,
    ("admin",)
).fetchone()

if usuario_existente:

    cursor.execute(
        """
        UPDATE usuarios
        SET
            nombre = ?,
            email = ?,
            password_hash = ?,
            id_rol = ?,
            estado = ?,
            modulo_inicial = ?
        WHERE usuario = ?
        """,
        (
            "Administrador General",
            "admin@sigem.com",
            password_hash,
            id_rol,
            "Activo",
            "dashboard_app",
            "admin"
        )
    )

else:

    cursor.execute(
        """
        INSERT INTO usuarios (
            usuario,
            nombre,
            email,
            password_hash,
            id_rol,
            estado,
            modulo_inicial
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
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
conn.close()

print("✅ ADMIN LISTO")
print("usuario: admin")
print("password: admin123")
