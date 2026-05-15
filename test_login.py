import sqlite3
from sigem_db import get_db_path

db_path = get_db_path("seguridad")

conn = sqlite3.connect(db_path)

cur = conn.cursor()

roles = [

    ("Admin", "Administrador del sistema"),
    ("Gerencia", "Gerencia general"),
    ("Compras", "Modulo compras"),
    ("Logistica", "Modulo logistica"),
    ("WMS", "Modulo almacen WMS"),
    ("Consulta", "Solo consulta")

]

for nombre_rol, descripcion in roles:

    cur.execute("""
        INSERT OR IGNORE INTO roles (
            nombre_rol,
            descripcion
        )
        VALUES (?, ?)
    """, (
        nombre_rol,
        descripcion
    ))

conn.commit()
conn.close()

print("✅ Roles insertados correctamente.")
