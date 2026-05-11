import streamlit as st
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "erp.db"


def crear_tablas(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY,
            nombre_rol TEXT,
            descripcion TEXT,
            estado TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            nombre TEXT,
            password_hash TEXT,
            estado TEXT,
            id_rol INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modulos (
            id_modulo INTEGER PRIMARY KEY,
            nombre_modulo TEXT,
            ruta TEXT,
            estado TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permisos_roles (
            id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
            id_rol INTEGER,
            id_modulo INTEGER
        )
    """)

    conn.commit()


def cargar_datos(conn):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO roles
        (id_rol, nombre_rol, descripcion, estado)
        VALUES
        (1, 'Admin', 'Administrador general', 'Activo')
    """)

    cursor.execute("""
        INSERT OR REPLACE INTO usuarios
        (usuario, nombre, password_hash, estado, id_rol)
        VALUES
        ('JCERVANTES', 'JOSE JUANCERVANTES', 'Roberto1', 'Activo', 1)
    """)

    modulos = [
        (1, "Inventarios", "inventarios", "Activo"),
        (2, "Compras", "compras", "Activo"),
        (3, "Logística", "logistica", "Activo"),
        (4, "WMS", "wms", "Activo"),
        (5, "Mantenimiento", "mantenimiento", "Activo"),
    ]

    for m in modulos:
        cursor.execute("""
            INSERT OR REPLACE INTO modulos
            (id_modulo, nombre_modulo, ruta, estado)
            VALUES (?, ?, ?, ?)
        """, m)

    permisos = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]

    for p in permisos:
        cursor.execute("""
            INSERT INTO permisos_roles (id_rol, id_modulo)
            VALUES (?, ?)
        """, p)

    conn.commit()


st.title("🛠️ Crear / reconstruir erp.db")

st.write("📂 Ruta encontrada:")
st.code(str(DB_PATH))

if DB_PATH.exists():
    st.write("📦 Base encontrada")
    st.write("📏 Tamaño actual bytes:")
    st.write(DB_PATH.stat().st_size)
else:
    st.warning("⚠️ No existe erp.db. Se creará en esta ruta.")

if st.button("Reconstruir erp.db"):
    conn = sqlite3.connect(DB_PATH)

    st.info("🔧 Creando tablas...")
    crear_tablas(conn)

    st.info("📥 Insertando datos base...")
    cargar_datos(conn)

    conn.close()

    st.success("✅ erp.db reconstruida correctamente")
    st.write("📏 Nuevo tamaño bytes:")
    st.write(DB_PATH.stat().st_size)

st.markdown("---")

if DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tablas = cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """).fetchall()

    st.subheader("📋 Tablas actuales")
    st.write([t[0] for t in tablas])

    for tabla in [t[0] for t in tablas]:
        st.markdown(f"### {tabla}")
        filas = cursor.execute(f"SELECT * FROM {tabla}").fetchall()
        st.write(f"Registros: {len(filas)}")
        st.write(filas)

    conn.close()
