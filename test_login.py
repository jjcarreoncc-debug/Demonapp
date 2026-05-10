from database import get_connection


conn = get_connection()
cur = conn.cursor()

print("\n===== TABLAS =====")

cur.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
""")

for row in cur.fetchall():
    print(row)


print("\n===== TOTAL MATERIALES =====")

cur.execute("""
    SELECT COUNT(*)
    FROM materiales
""")

print(cur.fetchone())


print("\n===== MATERIALES =====")

cur.execute("""
    SELECT
        codigo_material,
        descripcion,
        categoria,
        estatus
    FROM materiales
    LIMIT 20
""")

rows = cur.fetchall()

for row in rows:
    print(dict(row))


conn.close()

print("\n===== FIN TEST =====")
