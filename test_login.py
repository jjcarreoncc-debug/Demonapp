import sqlite3
import hashlib

conn = sqlite3.connect("sigem.db")
cursor = conn.cursor()

# ==========================================
# PASSWORD
# ==========================================

password = "admin123"

password_hash = hashlib.sha256(
    password.encode()
).hexdigest()

# ==========================================
# CREAR ROL ALL
# ==========================================

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

# ==========================================
# OBTENER ID ROL
# ==========================================

cursor.execute(
    """
    SELECT id_rol
    FROM roles
    WHERE nombre_rol = ?
    """,
    ("ALL",)
)

id_rol = cursor.fetchone()[0]

# ==========================================
# CREAR USUARIO ADMIN
# ==========================================

cursor.execute(
    """
    INSERT OR REPLACE INTO usuarios (
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

print("✅ ADMIN CREADO")
print("usuario: admin")
print("password: admin123")
