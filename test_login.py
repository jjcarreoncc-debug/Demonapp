import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from sigem_db import get_db_path


st.set_page_config(
    page_title="Reset Usuario Seguridad",
    layout="wide"
)


def generar_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


st.title("🔐 Reset Usuario Seguridad")

db_path = get_db_path("seguridad")

st.write("Base usada:")
st.code(db_path)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

st.subheader("Usuarios actuales")

df = pd.read_sql_query(
    """
    SELECT
        id_usuario,
        usuario,
        nombre,
        password_hash,
        id_rol,
        estado,
        bloqueado
    FROM usuarios
    """,
    conn
)

st.dataframe(df, use_container_width=True)

st.divider()

usuario = st.text_input("Usuario a actualizar", value="admin")
nuevo_password = st.text_input("Nueva contraseña", value="admin123", type="password")

if st.button("Actualizar contraseña y activar usuario", use_container_width=True):

    password_hash = generar_hash(nuevo_password)

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
        st.success("Usuario actualizado correctamente.")
        st.write("Ya puedes entrar con:")
        st.code(f"usuario: {usuario}\npassword: {nuevo_password}")

conn.close()
