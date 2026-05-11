import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def buscar_db():
    for db in BASE_DIR.glob("*.db"):
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
            """)
            tablas = [t[0] for t in cursor.fetchall()]
            conn.close()

            if "usuarios" in tablas or db.name == "erp.db":
                return db
        except Exception:
            pass

    return BASE_DIR / "erp.db"


DB_PATH = buscar_db()


def crear_tablas_base(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_rol TEXT UNIQUE,
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
            id_rol INTEGER,
            perfil TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modulos (
            id_modulo INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_modulo TEXT,
            ruta TEXT UNIQUE,
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


def seed_seguridad(conn):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO roles (
            id_rol,
            nombre_rol,
            descripcion,
            estado
        )
        VALUES (
            1,
            'Admin',
            'Administrador general del sistema',
            'Activo'
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios (
            usuario,
            nombre,
            password_hash,
            estado,
            id_rol,
            perfil
        )
        VALUES (
            'JCERVANTES',
            'JOSE JUANCERVANTES',
            'Roberto1',
            'Activo',
            1,
            'ALL'
        )
    """)

    modulos = [
        (1, "Inventarios", "inventarios", "Activo"),
        (2, "Compras", "compras", "Activo"),
        (3, "Logística", "logistica", "Activo"),
        (4, "WMS", "wms", "Activo"),
        (5, "Mantenimiento", "mantenimiento", "Activo"),
    ]

    for modulo in modulos:
        cursor.execute("""
            INSERT OR IGNORE INTO modulos (
                id_modulo,
                nombre_modulo,
                ruta,
                estado
            )
            VALUES (?, ?, ?, ?)
        """, modulo)

    permisos = [
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
    ]

    for id_rol, id_modulo in permisos:
        cursor.execute("""
            INSERT OR IGNORE INTO permisos_roles (
                id_rol,
                id_modulo
            )
            VALUES (?, ?)
        """, (id_rol, id_modulo))

    conn.commit()


def mostrar_tabla(conn, tabla):
    try:
        df = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
        st.subheader(f"📋 {tabla}")
        st.success(f"Registros: {len(df)}")
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"No pude leer tabla: {tabla}")
        st.exception(e)


def app():
    st.title("🧪 Reporte y actualización de seguridad")

    st.write("📂 Ruta donde encontró la base:")
    st.code(str(DB_PATH))

    st.write("📦 Existe:")
    st.write(DB_PATH.exists())

    if DB_PATH.exists():
        st.write("📏 Tamaño bytes:")
        st.write(DB_PATH.stat().st_size)

    conn = sqlite3.connect(DB_PATH)

    if st.button("Crear / actualizar usuarios, roles, perfil ALL y permisos"):
        crear_tablas_base(conn)
        seed_seguridad(conn)
        st.success("✅ Seguridad actualizada correctamente")

    st.markdown("---")

    crear_tablas_base(conn)

    mostrar_tabla(conn, "usuarios")
    mostrar_tabla(conn, "roles")
    mostrar_tabla(conn, "modulos")
    mostrar_tabla(conn, "permisos_roles")

    conn.close()


if __name__ == "__main__":
    app()
