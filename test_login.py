import streamlit as st
import hashlib

from database import get_connection


st.title("Crear ADMIN")

conn = get_connection()
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
    INSERT INTO roles (
        nombre_rol,
        descripcion
    )
    SELECT ?, ?
    WHERE NOT EXISTS (
        SELECT 1
        FROM roles
        WHERE nombre_rol = ?
    )
    """,
    (
        "ALL",
        "Acceso total sistema",
        "ALL"
    )
)

conn.commit()

# ==========================================
# OBTENER ID ROL
# ==========================================

row_rol = cursor.execute(
    """
    SELECT id_rol
    FROM roles
    WHERE nombre_rol = ?
    """,
    ("ALL",)
).fetchone()

id_rol = row_rol["id_rol"]

# ==========================================
# CREAR / ACTUALIZAR ADMIN
# ==========================================

row_user = cursor.execute(
    """
    SELECT id_usuario
    FROM usuarios
    WHERE usuario = ?
    """,
    ("admin",)
).fetchone()

if row_user is None:

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

else:

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

conn.commit()

st.success("✅ ADMIN creado / actualizado")

st.write("Usuario: admin")
st.write("Password: admin123")

conn.close()
