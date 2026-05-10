import streamlit as st
import hashlib
import pandas as pd

from database import get_connection


st.title("🔎 Test login admin")

usuario = "admin"
password = "admin123"
password_hash = hashlib.sha256(password.encode()).hexdigest()

conn = get_connection()

df = pd.read_sql_query(
    """
    SELECT
        u.id_usuario,
        u.usuario,
        u.nombre,
        u.password_hash,
        u.estado,
        u.id_rol,
        r.nombre_rol
    FROM usuarios u
    LEFT JOIN roles r
        ON u.id_rol = r.id_rol
    WHERE UPPER(u.usuario) = UPPER(?)
    """,
    conn,
    params=(usuario,)
)

st.dataframe(df, use_container_width=True)

st.write("Password escrito:", password)
st.write("Hash calculado:", password_hash)

if not df.empty:
    st.write("Hash en BD:", df["password_hash"].iloc[0])
    st.write(
        "¿Coincide?",
        df["password_hash"].iloc[0] == password_hash
    )

conn.close()
