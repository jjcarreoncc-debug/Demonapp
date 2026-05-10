import streamlit as st
import pandas as pd

from database import get_connection


st.title("🔎 CONSULTA TOTAL TABLA USUARIOS")

conn = get_connection()

# ==========================================
# ESTRUCTURA
# ==========================================

st.subheader("📘 Estructura tabla usuarios")

estructura_df = pd.read_sql_query(
    """
    PRAGMA table_info(usuarios)
    """,
    conn
)

st.dataframe(
    estructura_df,
    use_container_width=True
)

# ==========================================
# TODOS LOS DATOS
# ==========================================

st.subheader("📊 Datos completos usuarios")

usuarios_df = pd.read_sql_query(
    """
    SELECT *
    FROM usuarios
    """,
    conn
)

st.dataframe(
    usuarios_df,
    use_container_width=True
)

# ==========================================
# ROLES
# ==========================================

st.subheader("📊 Datos completos roles")

roles_df = pd.read_sql_query(
    """
    SELECT *
    FROM roles
    """,
    conn
)

st.dataframe(
    roles_df,
    use_container_width=True
)

# ==========================================
# JOIN USUARIO + ROL
# ==========================================

st.subheader("🔗 Usuarios + Roles")

join_df = pd.read_sql_query(
    """
    SELECT
        u.id_usuario,
        u.usuario,
        u.nombre,
        u.email,
        u.estado,
        u.modulo_inicial,
        r.id_rol,
        r.nombre_rol,
        r.descripcion
    FROM usuarios u
    LEFT JOIN roles r
        ON u.id_rol = r.id_rol
    """,
    conn
)

st.dataframe(
    join_df,
    use_container_width=True
)

conn.close()
