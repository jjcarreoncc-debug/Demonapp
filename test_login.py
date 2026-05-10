import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import hashlib


DB_PATH = Path(__file__).resolve().parent / "erp.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


st.title("🧪 Test SELECT Login")

usuario = st.text_input("Usuario de prueba", value="JCERVANTES")
password = st.text_input("Password de prueba", value="Roberto1", type="password")

if st.button("Probar login"):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    st.write("BD usada:")
    st.code(str(DB_PATH))

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
        WHERE UPPER(u.usuario) = UPPER(?)
        """,
        (usuario.strip(),)
    ).fetchone()

    conn.close()

    if row is None:
        st.error("❌ No encontró usuario")
    else:
        data = dict(row)

        st.success("✅ Usuario encontrado")
        st.write(data)

        password_bd = str(data["password_hash"]).strip()
        password_ingresado = str(password).strip()
        password_hash = hash_password(password_ingresado)

        st.write("Password BD:", password_bd)
        st.write("Password ingresado:", password_ingresado)
        st.write("Hash ingresado:", password_hash)

        if password_bd == password_ingresado:
            st.success("✅ Coincide password plano")

        elif password_bd == password_hash:
            st.success("✅ Coincide password hash")

        else:
            st.error("❌ No coincide password")
