import streamlit as st
import sqlite3
import hashlib
import pandas as pd

from sigem_db import get_db_path


st.set_page_config(
    page_title="Reset Admin",
    layout="wide"
)


def generar_hash(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def columna_existe(cur, tabla, columna):

    cur.execute(
        f"PRAGMA table_info({tabla})"
    )

    columnas = [
        x[1]
        for x in cur.fetchall()
    ]

    return columna in columnas


def agregar_columna(
    cur,
    tabla,
    columna,
    definicion
):

    if not columna_existe(
        cur,
        tabla,
        columna
    ):

        cur.execute(
            f"""
            ALTER TABLE {tabla}
            ADD COLUMN {columna} {definicion}
            """
        )


st.title("🔐 Reset Usuario Admin")

db_path = get_db_path("seguridad")

st.success(f"BD usada: {db_path}")

conn = sqlite3.connect(db_path)

cur = conn.cursor()

# =========================
# ASEGURAR COLUMNAS
# =========================

agregar_columna(
    cur,
    "usuarios",
    "password_hash",
    "TEXT"
)

agregar_columna(
    cur,
    "usuarios",
    "estado",
    "TEXT DEFAULT 'Activo'"
)

agregar_columna(
    cur,
    "usuarios",
    "id_rol",
    "INTEGER DEFAULT 1"
)

conn.commit()

# =========================
# MOSTRAR USUARIOS
# =========================

df = pd.read_sql_query(
    """
    SELECT *
    FROM usuarios
    """,
    conn
)

st.subheader("👤 Usuarios actuales")

st.dataframe(
    df,
    use_container_width=True
)

st.divider()

usuario = st.text_input(
    "Usuario",
    value="admin"
)

password = st.text_input(
    "Password",
    value="admin123",
    type="password"
)

if st.button(
    "🚀 Crear / Actualizar Admin",
    use_container_width=True
):

    try:

        password_hash = generar_hash(
            password
        )

        # =========================
        # CREAR SI NO EXISTE
        # =========================

        cur.execute(
            """
            INSERT OR IGNORE INTO usuarios
            (
                usuario,
                nombre,
                password_hash,
                estado,
                id_rol
            )
            VALUES
            (
                ?,
                ?,
                ?,
                'Activo',
                1
            )
            """,
            (
                usuario,
                "Administrador SIGEM",
                password_hash
            )
        )

        # =========================
        # ACTUALIZAR
        # =========================

        cur.execute(
            """
            UPDATE usuarios
            SET
                password_hash = ?,
                estado = 'Activo',
                id_rol = 1
            WHERE
                TRIM(UPPER(usuario))
                =
                TRIM(UPPER(?))
            """,
            (
                password_hash,
                usuario
            )
        )

        conn.commit()

        st.success(
            "✅ Usuario actualizado correctamente."
        )

        st.code(
            f"""
usuario: {usuario}
password: {password}
            """
        )

        st.rerun()

    except Exception as e:

        st.error(
            "❌ Error actualizando usuario"
        )

        st.exception(e)

conn.close()
