import streamlit as st
import pandas as pd

from database import get_connection


st.title("🔎 DATOS TABLA USUARIOS")

conn = get_connection()

# ==========================================
# USUARIOS
# ==========================================

usuarios_df = pd.read_sql_query(
    """
    SELECT *
    FROM usuarios
    """,
    conn
)

st.subheader("📊 TABLA USUARIOS")

st.dataframe(
    usuarios_df,
    use_container_width=True
)

# ==========================================
# ROLES
# ==========================================

roles_df = pd.read_sql_query(
    """
    SELECT *
    FROM roles
    """,
    conn
)

st.subheader("📊 TABLA ROLES")

st.dataframe(
    roles_df,
    use_container_width=True
)

# ==========================================
# JOIN
# ==========================================

join_df = pd.read_sql_query(
    """
    SELECT
        u.id_usuario,
        u.usuario,
        u.nombre,
        u.email,
        u.estado,
        r.nombre_rol
    FROM usuarios u
    LEFT JOIN roles r
        ON u.id_rol = r.id_rol
    """,
    conn
)

st.subheader("🔗 USUARIOS + ROLES")

st.dataframe(
    join_df,
    use_container_width=True
)

conn.close()
