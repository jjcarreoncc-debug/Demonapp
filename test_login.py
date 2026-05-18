import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from sigem_db import get_db_path


st.set_page_config(page_title="Reset Usuario", layout="wide")


def generar_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def columna_existe(cur, tabla, columna):
    cur.execute(f"PRAGMA table_info({tabla})")
    columnas = [x[1] for x in cur.fetchall()]
    return columna in columnas


def agregar_columna(cur, tabla, columna, definicion):
    if not columna_existe(cur, tabla, columna):
        cur.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")


st.title("🔐 Reset Usuario Seguridad")

db_path = get_db_path("seguridad")
st.code(db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

agregar_columna(cur, "usuarios", "password_hash", "TEXT")
agregar_columna(cur, "usuarios", "estado", "TEXT DEFAULT 'Activo'")
agregar_columna(cur, "usuarios", "bloqueado", "TEXT DEFAULT 'No'")
agregar_columna(cur, "usuarios", "intentos_login", "INTEGER DEFAULT 0")
agregar_columna(cur, "usuarios", "fecha_bloqueo", "TEXT")

conn.commit()

df = pd.read_sql_query("SELECT * FROM usuarios", conn)
st.dataframe(df, use_container_width=True)

usuario = st.text_input("Usuario", value="admin")
password = st.text_input("Nuevo password", value="admin123", type="password")

if st.button("Actualizar usuario", use_container_width=True):
    password_hash = generar_hash(password)

    cur.execute(
        """
        UPDATE usuarios
        SET
            password_hash = ?,
            estado = 'Activo',
            bloqueado = 'No',
            intentos_login = 0,
            fecha_bloqueo = NULL
        WHERE usuario = ?
        """,
        (password_hash, usuario)
    )

    conn.commit()

    if cur.rowcount == 0:
        st.error("No se encontró el usuario.")
    else:
        st.success("Usuario actualizado.")
        st.code(f"usuario: {usuario}\npassword: {password}")

conn.close()
