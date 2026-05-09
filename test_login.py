import streamlit as st
import hashlib

from database import get_connection


def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


st.title("🔐 Reset Admin")


conn = get_connection()

cursor = conn.cursor()


if st.button("Reset password admin a 1234"):

    cursor.execute(
        """
        UPDATE usuarios
        SET password_hash = ?,
            estado = 'Activo'
        WHERE usuario = 'admin'
        """,
        (
            hash_password("1234"),
        )
    )

    conn.commit()

    st.success(
        "✅ Password actualizado"
    )

    st.info(
        "Usuario: admin"
    )

    st.info(
        "Password: 1234"
    )


conn.close()
