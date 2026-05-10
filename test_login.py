
import streamlit as st
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def buscar_db_con_usuarios():
    for db_file in BASE_DIR.glob("*.db"):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name='usuarios'
            """)

            existe = cursor.fetchone() is not None
            conn.close()

            if existe:
                return str(db_file)

        except Exception:
            pass

    return str(BASE_DIR / "erp.db")


DB_PATH = buscar_db_con_usuarios()


def validar_login(usuario, password):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    usuario_normalizado = str(usuario).strip().upper()
    password_normalizado = str(password).strip()

    try:
        row = cursor.execute(
            """
            SELECT
                u.usuario,
                u.nombre,
                u.password_hash,
                u.estado,
                r.nombre_rol AS rol
            FROM usuarios u
            LEFT JOIN roles r
                ON u.id_rol = r.id_rol
            WHERE TRIM(UPPER(u.usuario)) = ?
            """,
            (usuario_normalizado,)
        ).fetchone()

    except Exception as e:
        conn.close()
        st.error("❌ Error consultando usuario")
        st.write("BD usada:", DB_PATH)
        st.exception(e)
        return None

    conn.close()

    if row is None:
        return None

    password_bd = str(row["password_hash"]).strip()
    password_hash = hash_password(password_normalizado)

    if password_bd != password_normalizado and password_bd != password_hash:
        return None

    return row
