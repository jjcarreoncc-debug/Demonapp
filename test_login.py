import streamlit as st
import hashlib

from database import get_connection


st.title("CREAR ADMIN")

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

row_rol = cursor.fetchone()

id_rol = row_rol[0]

# ==========================================
# VALIDAR USUARIO
# ==========================================

cursor.execute(
    """
    SELECT id_usuario
    FROM usuarios
    WHERE usuario = ?
    """,
    ("admin",)
)

row_user = cursor.fetchone()

# ==========================================
# INSERT / UPDATE
# ==========================================

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

st.success("✅ ADMIN creado")

st.write("Usuario: admin")
st.write("Password: admin123")

conn.close()
