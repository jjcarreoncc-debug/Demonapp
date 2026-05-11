import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "erp.db"


def reporte_usuarios_app():

    st.title("👥 Reporte de usuarios")

    conn = sqlite3.connect(DB_PATH)

    st.caption(f"BD usada: {DB_PATH}")

    try:
        df_usuarios = pd.read_sql_query("SELECT * FROM usuarios", conn)
        df_roles = pd.read_sql_query("SELECT * FROM roles", conn)

        st.success(f"Usuarios encontrados: {len(df_usuarios)}")

        if "id_rol" in df_usuarios.columns and "id_rol" in df_roles.columns:
            df = df_usuarios.merge(
                df_roles[["id_rol", "nombre_rol"]],
                on="id_rol",
                how="left"
            )
        else:
            df = df_usuarios

        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("❌ Error generando reporte")
        st.exception(e)

    finally:
        conn.close()


if __name__ == "__main__":
    reporte_usuarios_app()
