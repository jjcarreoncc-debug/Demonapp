import streamlit as st

from database import get_connection


st.title("TEST LOGIN SQL")

usuario = "admin"

conn = get_connection()
cursor = conn.cursor()

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
    (usuario,)
).fetchone()

st.write("RESULTADO:")
st.write(row)

conn.close()
