import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def buscar_db_usuarios():
    for db_path in BASE_DIR.glob("*.db"):
        try:
            conn = sqlite3.connect(db_path)
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
                return db_path

        except Exception:
            pass

    return None


def leer_tabla(conn, tabla):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {tabla}")
    filas = cursor.fetchall()
    columnas = [desc[0] for desc in cursor.description]
    return pd.DataFrame(filas, columns=columnas)


def reporte_usuarios_app():

    st.title("👥 Reporte de usuarios")

    db_path = buscar_db_usuarios()

    if db_path is None:
        st.error("❌ No encontré ninguna base con tabla usuarios.")
        return

    st.success(f"✅ Base encontrada: {db_path}")

    conn = sqlite3.connect(db_path)

    st.subheader("📋 Usuarios")
    df_usuarios = leer_tabla(conn, "usuarios")
    st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

    st.subheader("🧩 Roles")
    df_roles = leer_tabla(conn, "roles")
    st.dataframe(df_roles, use_container_width=True, hide_index=True)

    conn.close()


if __name__ == "__main__":
    reporte_usuarios_app()
