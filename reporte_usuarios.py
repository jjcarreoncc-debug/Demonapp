import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "erp.db"


def leer_tabla(conn, tabla):
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {tabla}")
    filas = cursor.fetchall()

    columnas = [desc[0] for desc in cursor.description]

    return pd.DataFrame(filas, columns=columnas)


def reporte_usuarios_app():

    st.title("👥 Reporte de usuarios")
    st.caption(f"BD usada: {DB_PATH}")

    try:
        conn = sqlite3.connect(DB_PATH)

        st.subheader("📋 Usuarios")

        df_usuarios = leer_tabla(conn, "usuarios")

        st.success(f"Usuarios encontrados: {len(df_usuarios)}")

        st.dataframe(
            df_usuarios,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        st.subheader("🧩 Roles")

        df_roles = leer_tabla(conn, "roles")

        st.success(f"Roles encontrados: {len(df_roles)}")

        st.dataframe(
            df_roles,
            use_container_width=True,
            hide_index=True
        )

        conn.close()

    except Exception as e:
        st.error("❌ Error generando reporte")
        st.exception(e)


if __name__ == "__main__":
    reporte_usuarios_app()
